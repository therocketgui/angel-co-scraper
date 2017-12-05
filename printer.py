import json
import re
from time import sleep

import csv
import datetime

def get_json():
	with open('jobs.json') as data_file: 
		data = json.load(data_file)
	return data

def convert_json_to_csv():
	jobs = get_json()

	now = datetime.datetime.now()
	date = str(now.day) + "-" + str(now.month) + "-" + str(now.year)
	filename='job-emails-'+date+'.csv'

	with open(filename, 'w') as csvfile:
		filewriter = csv.writer(csvfile, delimiter=',', quoting=csv.QUOTE_MINIMAL)
		filewriter.writerow(['email', 'fname', 'lname', 'position', 'confidence','picture', 'name', 'link', 'tagline', 'title', 'compensation', 'salary_min','salary_max', 'tags','location','employees','website'])

		for job in jobs['jobs']:
			for email in job['emails']:
				filewriter.writerow([ email['email'],email['fname'], email['lname'], email['position'], email['confidence'], job['picture'], job['name'], job['link'], job['tagline'], job['title'], job['compensation'],str(job['compensation_detailed']['price_low']), str(job['compensation_detailed']['price_high']), job['tags'], job['location'], job['employees'],job['website'],])

	return

if __name__ == "__main__":

	convert_json_to_csv()