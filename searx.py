import json
from urllib.request import urlopen, Request
from urllib.parse import urlencode, quote_plus, quote
from urllib.error import HTTPError, URLError
from random import randint
import requests
from bs4 import BeautifulSoup
import re
from time import sleep
import ssl
import csv
import datetime
import random
import time
# INFOS #

# Search API : https://asciimoo.github.io/searx/dev/search_api.html

# Infos
# The searX API direct call Google, Bing and Yahoo Search APIs without any limits / securities + it's anonymous

class Google():

    def __init__(self, q):
        self.q = self.clean(q)
        return

    def clean(self, url):
        url = url.replace('https://www.', '')
        url = url.replace('http://www.', '')
        url = url.replace('https://', '')
        url = url.replace('http://', '')
        url = url.replace('www.', '').replace('ww7.', '').replace('ww38', '.')
        return url.split('/')[0]

    def create_url(self):
        rand_base = ['https://searx.xyz', 'https://searx.me', 'https://searx.site']
        encoded_query = urlencode({'q' : 'site:linkedin.com '+self.q})
        url = random.choice(rand_base) + "/search?" + encoded_query
        return url

    def call_url(self):
        url = self.create_url()

        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE

        #print("Query URL :")
        #print(url)
        response = urlopen(url, context=ctx)
        string = response.read().decode('utf-8')
        soup = BeautifulSoup(string, 'lxml')

        # print('Scraping... '+str(url)+'\n')
        return soup

    def get_lead(self, title, link, description):

      _spl = title.split(' - ')
      # print(_spl)
      first_name = _spl[0].split(' ')[0].capitalize()
      last_name = _spl[0].split(' ', 1)[1].capitalize()

      job_title = _spl[1]
      company = _spl[2].replace(' | LinkedIn', '').replace(' ...', '').replace(' …', '')

      return {'first_name': first_name, 'last_name': last_name, 'job_title': job_title, 'company': company, 'link': link}

    def leads(self):
        leads = []

        try:
          soup = self.call_url()
        except:
          print('[SearX 403 - Sleeping for 90 seconds]')
          time.sleep(90)
          try:
            soup = self.call_url()
          except:
            print('[SearX 403 x2 - Sleeping for 180 seconds]')
            time.sleep(180)
            soup = self.call_url()

        for attrs in soup.find_all("div", {"class":"result result-default"}):
            try:
                title = str(attrs.h4.text)
                description = str(attrs.p.text)
                link = str(attrs.a['href'])

                # print(title)
                # print(description)
                # print(link)
                # print('\n')

                if '/in/' in link:
                  leads.append(self.get_lead(title, link, description))

            except Exception as e:
                # print(e)
                # TO FIX ?
                pass

        return leads

    def run(self):
      return self.leads()

if __name__ == "__main__":

    scrap = Google("https://www.postman.com")
    print(scrap.run())
