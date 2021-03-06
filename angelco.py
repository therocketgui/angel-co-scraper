
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
import selenium.webdriver.support.ui as ui
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

import ssl
from urllib.request import urlopen, Request
from urllib.parse import urlencode, quote_plus, quote
from urllib.error import HTTPError, URLError

#from browsermobproxy import Server
#from xlsxlib import Excel
import time
import re
import os
import json
import random
from random import shuffle

import csv
import datetime
import requests

import traceback


from env import _path_to_mozilla, email_address, password_text
from searx import Google


class Angelco():

  def __init__(self, keywords):

    options = Options()
    options.add_argument("--headless")
    self.driver = webdriver.Firefox(firefox_options=options, executable_path=_path_to_mozilla)
    # self.driver = webdriver.Firefox(executable_path=_path_to_mozilla)
    self.driver.implicitly_wait(10)
    self.clever_print("Firefox Headless Browser Invoked")

    self.search_uri_str = self.handle_uri(keywords)

    return

  def handle_uri(self, keywords):
    uri = 'https://angel.co/jobs#find/f!%7B%22roles%22%3A%5B%22Growth%20Hacker%22%5D%2C%22locations%22%3A%5B%221653-Los%20Angeles%2C%20CA%22%5D%7D'
    return uri

  def clever_print(self, message):
    # Print and Log
    print(self.curtime()+"~ "+str(message))
    # self.log+= self.curtime()+"~ "+str(message)
    return

  def curtime(self):
    return '[' + time.strftime("%d/%m/%Y")+ ' - ' + time.strftime("%H:%M:%S") + '] '

  def start(self):

    return

  def quit(self):
    print('Quit Driver')
    self.driver.quit()
    self.short_sleep()
    return

  def get(self, url):
    self.driver.get(url)
    self.clever_print('Getting: '+str(url))
    self.medium_sleep()
    return

  def very_short_sleep(self):
    # Random short sleep time
    r = random.uniform(0.08, 0.13)
    time.sleep(r)
    return

  def short_sleep(self):
    # Random short sleep time
    r = random.uniform(0.6, 1.2)
    time.sleep(r)
    return

  def medium_sleep(self):
    # Random medium sleep time
    r = random.uniform(1.6, 2.2)
    time.sleep(r)
    return

  def large_sleep(self):
    # Random medium sleep time
    r = random.uniform(3, 6)
    time.sleep(r)
    return

  def scroll_bottom(self):
    # Scroll to bottom of a page
    self.clever_print('Revealing all jobs...')
    for scroll in range(0,1):
      self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
      self.short_sleep()

    self.medium_sleep()
    self.driver.execute_script("window.scrollTo(0, -document.body.scrollHeight);")
    return

  def login(self):
    self.clever_print('Login Start...')
    self.get('https://angel.co/login')

    div_login = self.driver.find_element_by_class_name("standard_login")
    email = div_login.find_element_by_name('user[email]')
    password = div_login.find_element_by_name('user[password]')

    for character in email_address:
      email.send_keys(character)
      self.very_short_sleep()
    self.medium_sleep()

    for character in password_text:
      password.send_keys(character)
      self.very_short_sleep()
    self.medium_sleep()

    div_login.find_element_by_class_name("c-button").click()
    self.large_sleep()
    self.clever_print('Login Successfull...')
    return

  def search_uri(self):
    # Before figuring out the search url structure
    self.get(self.search_uri_str)
    return

  def handle_compensation(self, compensation):

    if 'No Salary' in compensation:
      _type = {'currency': None}
      _compensation = {'price_low': None, 'price_high': None}
    else:
      _type = {'currency': compensation.strip().split()[0][0]}
      prices = compensation.split(' – ')
      price_low = int(prices[0].replace(_type['currency'], '').replace('K', '000'))
      price_high = int(prices[1].split(' · ')[0].replace(_type['currency'], '').replace('K', '000'))
      _compensation = {'price_low':price_low, 'price_high':price_high}

    if 'No Equity' in compensation:
      _equity = {'equity': False}
    else:
      _equity = {'equity': True}

    return {**_type, **_compensation, **_equity}

  def search_scrape_job(self, job):
    #init
    job_link=None
    picture=None
    link=None
    name=None
    tagline=None
    title=None
    compensation=None
    compensation_detailed=None
    tags=None
    location=None
    employees=None
    website=None
    job_data=None

    soup = BeautifulSoup(job.get_attribute('outerHTML'), "html.parser")

    job_link = soup.select_one('a.startup-link')['href']
    picture = soup.select_one('div.browse-table-row-pic.js-browse-table-row-pic').select_one('img')['src']
    link = soup.select_one('a.startup-link')['href']
    name = soup.select_one('a.startup-link').text.strip()
    compensation = soup.select_one('div.collapsed-compensation').text.strip()
    compensation_detailed = self.handle_compensation(compensation)
    tags = soup.select_one('div.collapsed-tags').text.strip()

    title = soup.select_one('div.collapsed-title').text.strip()
    tagline = soup.select_one('div.tagline').text.strip()
    location = soup.select_one('div.locations').text.strip()
    employees = soup.select_one('div.employees').text.strip().replace(' employees', '')
    website = soup.select_one('a.website-link')['href']

    return {'job_link':job_link, 'picture':picture, 'link':link, 'name':name, 'tagline':tagline, 'title':title, 'compensation':compensation, 'compensation_detailed':compensation_detailed, 'tags':tags, 'location':location, 'employees':employees, 'website':website}

  def get_page_data(self, url):
    self.get(url)
    soup = BeautifulSoup(self.driver.page_source, "html.parser")

    try:
      company_description = {'description': soup.select_one('div.js-preamble').text}
    except:
      company_description = {'description': None}

    # Handle fundings format
    try:
      fundings_string = soup.find_all("div",{"class":"vital s-vgBottom1 tiptip"})[1].text.strip()
      # print(fundings_string)
      date = fundings_string.split('in ')[1].split('.')[0].strip()
      _type = fundings_string.strip().split()[0][0]
      amount_string = fundings_string.split(' ')[0]
      if 'M' in amount_string:
        amount = int(amount_string.replace('M', '').replace(_type, '')) * 1000000
      elif 'K' in amount_string:
        amount = int(amount_string.replace('K', '').replace(_type, '')) * 1000

      series = fundings_string.split(' ', 1)[1].split(' in')[0]

      fundings = {'date': date,'type': series,'amount': amount,'currency': _type}
    except:
      fundings = {'date': None,'type': None,'amount': None,'currency': None}

    socials = {'twitter': None}
    try:
      socials = {'twitter':soup.select_one('a.twitter-link')['href']}
    except:
      pass

    tags = []

    # Test all the divs as it may appear in different positions
    try:
      for sub_div in soup.find_all("div", {"class": "vital s-vgBottom1"}):
        if sub_div.find("div", {"class": "fontello-tag"}) is not None:
          for tag in sub_div.find_all('a'):
            tags.append(tag.text)
    except Exception as e:
      print(e)

    return {**company_description, **{'fundings': fundings}, **{'socials': socials}, **{'tags': tags}}

  def get_extra(self, data):
    for job in data:
      self.clever_print('Getting Extra for: '+job['name'])
      job['extra'] = self.get_page_data(job['link'])
      self.short_sleep()
    return data

  def get_people(self, data):
    for job in data:
      _peoples = []

      people = Google(job['website'])
      peoples = people.run()

      for p in peoples:
        if p['company'].lower()[:6] == job['name'].lower()[:6]:
          _peoples.append(p)

      job['peoples'] = _peoples

    return data

  def search_scrape(self):
    try:
      # Main Scraper Function
      self.clever_print('Starting Scraping...')
      job_list=[]

      self.search_uri()
      self.scroll_bottom()
      self.large_sleep()

      # bs4
      container = self.driver.find_element_by_class_name("startup-container")
      jobs = container.find_elements_by_class_name("job_listings")
      # iterate on each job
      for job in jobs:
        try:
          # self.driver.execute_script("arguments[0].scrollIntoView();", job)
          # Get infos
          job_data = self.search_scrape_job(job)
          self.clever_print('Getting '+job_data['name']+' job data...')

          self.print_json(job_data)
          job_list.append(job_data)
        except Exception as e:
          self.clever_print(e)
          pass

      # Get extra data optional
      job_list_extra = self.get_extra(job_list)
      # Get people from the company
      job_list_people = self.get_people(job_list_extra)

    except Exception as e:
      self.clever_print(e)
      self.clever_print('Quitting due to issue...')
      traceback.print_exc()
    finally:
      self.quit()

    return job_list_extra

  def get_json(self):
    with open('jobs.json') as data_file:
      data = json.load(data_file)
    return data

  def print_json(self,job):

    # retrieive the data stored and the local_id list
    data = self.get_json()
    data['jobs'].append(job)
    # write and store the data in the json
    with open('jobs.json', 'w') as f:
      json.dump(data, f, indent=4)
    return

def get_jobs(keywords):
  angel = Angelco(keywords)
  angel.login()
  company_list = angel.search_scrape()

  print(json.dumps(company_list, indent=4))
  return

if __name__ == "__main__":
  get_jobs(["Growth Manager", "San Fransisco"])

