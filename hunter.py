import json
import re
from time import sleep

from pyhunter import PyHunter

import ssl
import csv
import datetime

# Hunter class to find all emails associated to a TLD

# Change API key by your key.

# /!\ Be aware that each requests will cost $$$
# /!\ Find more at: https://hunter.io/pricing

class Hunter():

	def __init__(self):
		self.api_key = os.environ['HUNTER_API_KEY']
		return

	def find_email(self,tld):
		hunter = PyHunter(self.api_key)
		response = hunter.domain_search(company=tld)
		return response

	def reformate_json(self, response):

		data = []

		for r in response['emails']:
			email = r['value']
			type_r = r['type']
			confidence = r['confidence']

			if r['first_name'] != 'None':
				fname = r['first_name']
			else:
				fname = ''

			if r['last_name'] != 'None':
				lname = r['last_name']
			else:
				lname = ''
			
			position = r['position']

			row = {'email':email, 'type':type_r, 'confidence':confidence, 'fname':fname, 'lname':lname, 'position':position}

			data.append(row)

		return data

	def get_json(self):
		with open('jobs.json') as data_file: 
			data = json.load(data_file)
		return data

	def get_tld(self, website):
		tld = website.replace("http://www.", "").replace("https://www.", "").replace("http://", "").replace("https://", "").replace("/", "")
		return tld

	def emails(self,website):
		tld=self.get_tld(website)
		response = self.find_email(tld)
		data = self.reformate_json(response)

		return data

	def search_and_save(self):
		data = self.get_json()
		for d in data['jobs']:
			if 'emails' not in d:
				emails = self.emails(d['website'])
				d['emails'] = emails
				with open('jobs.json', 'w') as f:
					json.dump(data, f, indent=4)
		return

if __name__ == "__main__":

	s = Hunter()
	s.search_and_save()

