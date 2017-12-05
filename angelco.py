
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
import selenium.webdriver.support.ui as ui
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

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


class Angelco():

	def __init__(self):
		# Launch PhantomJS or Chromium
		self.driver = webdriver.Chrome(os.environ['PATH_TO_CHROMIUM'])
		#self.driver = webdriver.PhantomJS("/Users/guillaumedesa/Documents/phantomjs/bin/phantomjs")
		self.driver.implicitly_wait(10)
		
		time.sleep(1)

		return

	def quit(self):
		print('Quit Driver')
		self.driver.quit()
		self.short_sleep()
		return  

	def get(self, url):
		self.driver.get(url)
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
		print('Scrolling...')
		for scroll in range(0,15):
			self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
			self.short_sleep()

		self.medium_sleep()
		self.driver.execute_script("window.scrollTo(0, -document.body.scrollHeight);")
		return

	def login(self):
		self.get('https://angel.co/login')

		div_login = self.driver.find_element_by_class_name("standard_login")
		email = div_login.find_element_by_name("user[email]")
		password = div_login.find_element_by_name("user[password]")

		email_address = os.environ['ANGEL_LOGIN_ID']
		for character in email_address:
			email.send_keys(character)
			self.very_short_sleep()
		self.medium_sleep()

		password_text = os.environ['ANGEL_LOGIN_PWD']
		for character in password_text:
			password.send_keys(character)
			self.very_short_sleep()
		self.medium_sleep()  

		div_login.find_element_by_class_name("c-button").click()  
		self.large_sleep()
		return

	def search_uri(self):
		# Before figuring out the search url structure
		self.get('https://angel.co/jobs#find/f!%7B%22roles%22%3A%5B%22Marketing%22%5D%2C%22types%22%3A%5B%22internship%22%5D%2C%22locations%22%3A%5B%221842-Paris%2C%20FR%22%5D%7D')
		return

	def handle_compensation(self, compensation):
		char_list = list(compensation)
		if char_list[10] == 'k':
			# Retrieve prices and shares (if <£100K)
			price_low = char_list[1]+char_list[2]
			price_high = char_list[8]+char_list[9]
			#share_low = char_list[14]+char_list[15]+char_list[16]
			#share_high = char_list[20]+char_list[21]+char_list[22]
		else:
			# Retrieve prices and shares (if >=£100K)
			price_low = char_list[1]+char_list[2]+char_list[3]
			price_high = char_list[9]+char_list[10]+char_list[11]
			#share_low = char_list[16]+char_list[17]+char_list[18]
			#share_high = char_list[22]+char_list[23]+char_list[24]
		compensation_detailed = {'price_low':price_low, 'price_high':price_high}
		return compensation_detailed

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

		#get
		job_link = job.find_element_by_class_name("browse-table-row-pic").find_element_by_css_selector('a').get_attribute('href')
		picture = job.find_element_by_class_name("browse-table-row-pic").find_element_by_css_selector('a').find_element_by_css_selector('img').get_attribute('src')
		link = job.find_element_by_class_name("startup-link").get_attribute('href')
		name = job.find_element_by_class_name("startup-link").text
		tagline = job.find_element_by_class_name("tagline").text
		title = job.find_element_by_class_name("collapsed-title").text
		compensation = job.find_element_by_class_name("collapsed-compensation").text
		compensation_detailed = self.handle_compensation(compensation)
		tags = job.find_element_by_class_name("collapsed-tags").text
		location = job.find_element_by_class_name("locations").text
		employees = job.find_element_by_class_name("employees").text
		website = job.find_element_by_class_name("website-link").get_attribute('href')
		job_data = {'job_link':job_link, 'picture':picture, 'link':link, 'name':name, 'tagline':tagline, 'title':title, 'compensation':compensation, 'compensation_detailed':compensation_detailed, 'tags':tags, 'location':location, 'employees':employees, 'website':website}
 
		return job_data

	def search_scrape(self):
		# Main Scraper Function
		job_list=[]
		self.search_uri()
		self.scroll_bottom()
		self.large_sleep()
		container = self.driver.find_element_by_class_name("startup-container")
		jobs = container.find_elements_by_class_name("job_listings")
		for job in jobs:
			try:
				self.driver.execute_script("arguments[0].scrollIntoView();", job)
				job_data = self.search_scrape_job(job)
				print(job_data)
				print('\n')
				self.print_json(job_data)
				job_list.append(job_data)
			except Exception as e:
				print(e)
				pass
		self.quit()
		return job_list

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

	def print_csv(self):
		now = datetime.datetime.now()
		date = str(now.day) + "-" + str(now.month) + "-" + str(now.year)
		filename='jobs-'+date+'.csv'

		jobs = self.get_json()

		with open(filename, 'w') as csvfile:
			filewriter = csv.writer(csvfile, delimiter=',', quoting=csv.QUOTE_MINIMAL)
			filewriter.writerow(['picture', 'name', 'link', 'tagline', 'title', 'salary_min','salary_max', 'tags','location','employees','website'])

			for job in jobs['jobs']:
				filewriter.writerow([job['picture'], job['name'], job['link'], job['tagline'], job['title'], str(job['compensation_detailed']['price_low']), str(job['compensation_detailed']['price_high']), job['tags'], job['location'], job['employees'],job['website'],])

		return

if __name__ == "__main__":
	angel = Angelco()
	angel.login()
	company_list = angel.search_scrape()
	angel.print_csv()
