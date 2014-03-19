#!/usr/bin/python

#READ ME 
#Data will be loaded on a yearly basis. This script takes in an argument, year and will automatically return the result for the whole of that year
#Run python currency_scrape.py [year]
#

from bs4 import BeautifulSoup
from urllib2 import urlopen
from selenium import webdriver
import unicodecsv as csv
import datetime
import sys
import re

BASE_URL = "http://www.stproperty.sg"
 
BROWSER = webdriver.Firefox()

def main():

  first_name_chars = get_char_from_args() or ["a"]
  
  print first_name_chars

  for first_name_char_index,first_name_char in enumerate(first_name_chars):
    print "Searching by First Name begining with",first_name_char,"in ascending order"
    current_page_number = 1

    url = get_url_for_(first_name_char,current_page_number)
    last_page = get_last_page_of_agent_lists(url) or 1

    while(current_page_number <= last_page):
      print "Scraping page {current_page} of {last_page}".format(current_page=current_page_number,last_page=last_page)
      url = get_url_for_(first_name_char,current_page_number)
      write_agent_lists_to_csv(url,first_name_char)
      current_page_number += 1
  
  BROWSER.quit()


def write_to_csv(file_name,arr_objs):
  with open(file_name, 'wb') as csvfile:
    csv_writer = csv.writer(csvfile,encoding="utf-8")
    for arr_obj in arr_objs:
      try:
        csv_writer.writerow(arr_obj)
      except UnicodeEncodeError:
        print "cant write ",arr_obj," into file"   
      

def get_url_for_(first_name_char,current_page_number):
  return BASE_URL + "/property-agent/search-by-firstname/first-name-{char}/page{number}/size-50/sort-firstname-asc" .format(char=first_name_char,number=current_page_number)
   

def get_agent_profile_link(agent_div):
  agent_links = agent_div.find(class_="ca-sr-item-links")
  return BASE_URL + agent_links.find("a").attrs["href"]

def get_agent_(attr,agent_div):
  try:
    return agent_div.find(itemprop=attr).text
  except AttributeError:
    return None

def get_agent_phone_number(agent_profile_url):
  try:
    BROWSER.get(agent_profile_url)
    ab_contact_elem = BROWSER.find_element_by_class_name("ab-contact-number")
    elem_soup = BeautifulSoup(ab_contact_elem.get_attribute("innerHTML"))
    link_id = elem_soup.find("a").attrs["id"]
    phone_number_elem = BROWSER.find_element_by_id(link_id)
    phone_number_elem.click()
    return phone_number_elem.text
  except:
    return "-"

def get_char_from_args():
  try:
    args = sys.argv   
    del args[0]
    return args
  except IndexError:
    print "No arguments were passed"
    return None

def get_last_page_of_agent_lists(url):
  html = urlopen(url).read()
  soup = BeautifulSoup(html)
  pages_div = soup.find_all(class_="page")
  last_page_div = pages_div[len(pages_div)-1]
  last_page_url = last_page_div.find("a").attrs["href"] 
  last_current_page_number = re.search("page(\d+)", last_page_url).group(1)
  return int(last_current_page_number)

def get_agent_id_from(agent_profile_link):
  try:
    re_expression = re.compile('\d+')
    agent_id = re_expression.findall(agent_profile_link)[-1]
  except :
    return "Nil"
  return agent_id

def get_agent_details_from(agent_div):
  agent_name = get_agent_("name",agent_div)
  agent_job_title = get_agent_("jobTitle",agent_div)
  agent_company = get_agent_("worksFor",agent_div)
  agent_profile_link = get_agent_profile_link(agent_div)
  agent_phone_number = get_agent_phone_number(agent_profile_link)
  agent_id = get_agent_id_from(agent_profile_link)
  return [agent_id, agent_name,agent_job_title,agent_company,agent_profile_link,agent_phone_number]


def write_agent_lists_to_csv(url,first_name_char):
  html = urlopen(url).read()
  soup = BeautifulSoup(html)
  agent_lists = []
  agents_div = soup.find_all(class_="ca-sr-item")
  for agents_div_index,agent_div in enumerate(agents_div):
    agent_lists.append(get_agent_details_from(agent_div))
  write_to_csv("agent_list_{char}.csv".format(char=first_name_char), agent_lists)    


if  __name__ =='__main__':
  main()






















