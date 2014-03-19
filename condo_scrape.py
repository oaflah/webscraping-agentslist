from urllib2 import urlopen
from bs4 import BeautifulSoup
import unicodecsv as csv


BASE_URL = "http://www.stproperty.sg"
RELATIVE_FIRST_PAGE_URL = "/property-for-rent/condo-for-rent/"
MAX_ITERATIONS = 1000


def setup():
	iteration = 1
	soup = get_soup (BASE_URL + RELATIVE_FIRST_PAGE_URL)
	csv_file = open("condos.csv", "wb")
	csv_writer = csv.writer(csv_file,encoding="utf-8")
	headers = ["Condo Name", "District", "Date Posted", "Agent Id", "Price", "Beds", "Bathrooms", "Sq Feet", "Sq Meter"]
	csv_writer.writerow(headers)
	scrape_page(soup, iteration, csv_file, csv_writer)


def scrape_page(soup, iteration, csv_file, csv_writer):

	condos = soup.find_all('div', {"class":"sr-e-wrapper"})

	for condo in condos:
		details_array = get_condo_details(condo)
		csv_writer.writerow(details_array)
		
	next_page = check_next_page_exists(soup)
	if next_page and iteration < MAX_ITERATIONS:
		iteration+=1
		soup =  get_soup(BASE_URL + next_page);
		scrape_page(soup, iteration, csv_file, csv_writer)
	else:
		csv_file.close()
		print ("Done!")

def get_condo_details (condo):
	
	#condo name and district
	full_title = condo.find('h2').text
	condo_name = full_title[:full_title.find("(")]
	district = full_title[full_title.find("(") + 1: full_title.find(")")]

	#date, agent_id, price
	date_name_price = condo.find('div', {"class" :"sr-e-datenameprice"})
	date_name = date_name_price.find("h4")
	date = date_name.text[10:].split("  ")[0]
	agent_id_link = date_name.find("a")
	if agent_id_link:
		agent_id_url = agent_id_link.get('href')
		agent_id = agent_id_url[agent_id_url.rfind("/")+1:]
	else:
		agent_id_url = ""
		agent_id = ""
	price = date_name_price.find('h3').text



	#beds and bathrooms
	beds_el = condo.find(class_ = "sr-e-bedrooms")
	if beds_el:
		beds = beds_el.next_sibling.text
	else:
		beds = "0"

	bathrooms_el = condo.find(class_ = "sr-e-bathrooms")
	if bathrooms_el:
		bathrooms = bathrooms_el.next_sibling.text
	else:
		bathrooms = "0"

	#area
	[sq_ft, sq_m] =  condo.find(class_= "sr-e-info").find('a').text.split('/')

	print condo_name, district, date, agent_id, price
	return [condo_name, district, date, agent_id, price, beds, bathrooms, sq_ft, sq_m]




def get_soup (url):
	html =  urlopen(url).read()
	soup = BeautifulSoup (html)
	return soup

def check_next_page_exists(soup):
	next_links = soup.find_all("a", {"rel":"next"})
	if next_links:
		return next_links[0]['href']
	return False

def getOneCondo ():
	soup = BeautifulSoup(urlopen("http://www.stproperty.sg/property-for-rent/condo-for-rent").read())
	condo = soup.find_all('div', {"class":"sr-e-wrapper"})[0]

	return condo


