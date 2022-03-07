import requests
import pandas as pd
import urllib
from urllib import request, response
from bs4 import BeautifulSoup
import scrapy
from scrapy.crawler import CrawlerProcess
from scrapy.selector import Selector
from selenium import webdriver
import time
import csv


class RentHouses(scrapy.Spider):
	def __init__(self):
		self.base_url = 'https://www.rightmove.co.uk/property-to-rent/find.html?'
		self.header = {
			'User-Agent' : 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:96.0) Gecko/20100101 Firefox/96.0'
		}
		self.soup = None
		self.total_num_results = 0
		self.current_page = 0
		self.apartment_info_list = []

	def request_url(self, params):
		url = self.base_url + urllib.parse.urlencode(params)
		r = requests.get(url)
		text = r.text
		soup = BeautifulSoup(text, 'html.parser')
		self.soup = soup
		print(url)

	# def print_num_results(self):
	# 	num_results = self.soup.find_all('div', {'class': 'searchHeader-title'})
	# 	print(f'num_results: {num_results}')

	def get_num_results(self):
		num_results = self.soup.find('span', {'class': 'searchHeader-resultCount'}).text.strip()
		num_results = int(num_results)
		self.total_num_results = num_results

	def check_is_next_page(self):
		is_next_page = False
		if self.total_num_results > len(self.apartment_info_list):
			is_next_page = True

		return is_next_page

	def get_apartment_info(self, params):
		self.request_url(params)
		self.get_num_results()

		is_next_page = True
		while is_next_page:
			self.request_url(params)
			self.current_page += 1
			print(f'crawling page: {self.current_page}')
			self.total_num_results += 1
			single_page_info_list = self.get_single_page_info()
			self.apartment_info_list.extend(single_page_info_list)
			print(f'len_apartment_info_list: {len(self.apartment_info_list)}')
			is_next_page = self.check_is_next_page()
			print(f'is_next_page: {is_next_page}')
			print(f'total_num_results: {self.total_num_results}')
			# update param's index
			params['index'] = str(24 * self.current_page)
			print(f"index: {params['index']}")
			print()

	def get_single_page_info(self):
		single_page_info_list = []
		apartment_element_list = self.soup.find_all('div', {'class': 'l-searchResult is-list'})
		# loop over apartment_element_list
		for apartment_element in apartment_element_list:
			house_type = apartment_element.find('h2', 'propertyCard-title').text.strip()
			description_tag = apartment_element.find('div', 'propertyCard-description').text.strip()
			price_tag = apartment_element.find('span', 'propertyCard-priceValue').text.strip()
			phone_tag = apartment_element.find('a', 'propertyCard-contactsPhoneNumber').text.strip()
			address_tag = apartment_element.find('meta', {'itemprop': 'streetAddress'})['content']
			added_date_tag = apartment_element.find('span', 'propertyCard-branchSummary-addedOrReduced').text.strip()
			agent_tag = apartment_element.find('span', 'propertyCard-branchSummary-branchName').text.strip()
			link = 'https://www.rightmove.co.uk' + apartment_element.find('a', {'class': 'propertyCard-additionalImgs'}, href=True)['href']
			apartment_info = [house_type, description_tag, price_tag, phone_tag, address_tag, added_date_tag, agent_tag, link]
			single_page_info_list.append(apartment_info)
		print(f'finish get_single_page_info')

		return single_page_info_list


# initialize RentHouse
rent_crawler = RentHouses()
# define params
params = {
	'searchType': 'RENT',
	'locationIdentifier': 'REGION^1163',
    'minBedrooms': '2',
	'minPrice': '500',
	'maxPrice': '800',
	'radius': '5.0',
	'index': '',
	'propertyTypes': 'detached,semi-detached,terraced,flat',
	'includeLetAgreed': 'false',
	'mustHave': '',
    'dontShow': 'student,houseShare',
    'furnishTypes': '',
	'keywords': ''
}
# request url with params
# rent_crawler.request_url(params)
rent_crawler.get_apartment_info(params)
df = pd.DataFrame(rent_crawler.apartment_info_list, columns=['ouse_type', 'description_tag', 'price_tag', 'phone_tag', 'address_tag', 'added_date_tag', 'agent_tag', 'link'])
df = df.replace(to_replace=[r"\\t|\\n|\\r", "\t|\n|\r"], value=["", ""], regex=True)
adjusted = pd.set_option("display.expand_frame_repr", False)
print(df)

