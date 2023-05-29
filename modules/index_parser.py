# -*- coding: utf-8 -*-
from queue import Queue
import sys
from bs4 import BeautifulSoup
import re
import logging
import json
from datetime import datetime
import time
from selenium.webdriver.common.by import By
from .details_parser import CarDetailsParser

YAD2_TABLE_LIST = 'feed_list'
LOG_FILENAME = 'webScrapper.log'
# format = '%(asctime)s %(name)-15s %(levelname)-8s %(processName)-10s[%(process)d]%(funcName)10s: %(message)s'
format = '%(timestamp)s  %(name)s  %(level)s  %(module)s  %(lineno)s  %(message)s'
logging.basicConfig(filename=LOG_FILENAME, format=format, level=logging.CRITICAL)
logger = logging.getLogger('indexParser')

recordMapping = ['property_type', 'region', 'address', 'price', 'rooms', 'floor', 'date']
recordOriginals = ['סוג הנכס', 'אזור בארץ', 'כתובת', 'מחיר', "חד'", 'קומה', 'תאריך']

category_map = {"realestate": "Residential", "business": "Commercial", "cars": "Cars"}

nondigitMatcher = re.compile("[^\d]")
propertyIdMatcher = re.compile(r'(\?NadlanID=(?P<propertyID>[^\s&]+))')
pageNameFinder = re.compile(r'(cars|realestate|business)')
currencyMap = "./db/currencyMap.json"

currencyMapData = None
currencySymbols = None

try:
    with open(currencyMap, 'r') as f:
        currencyJsonData = f.read()
        currencyMapData = json.loads(currencyJsonData)
        currencySymbols = currencyMapData.keys()

except Exception as e:
    logger.error("Currency mapping couldn't be parsed")
    sys.exit(1)

proxies = {
    'http': "socks5://127.0.0.1:9050",
    'https': "socks5://127.0.0.1:9050"
}

headers = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:61.0) Gecko/20100101 Firefox/61.0"
}
rootUrl = "http://www.yad2.co.il"


class Yad2IndexParser:
    def __init__(self, html_manager):
        self.html_manager = html_manager
        self.data_queue = Queue()
        self.car_details_parser = CarDetailsParser(logger)

    def get_soup(self, html_doc):
        soup = None
        try:
            soup = BeautifulSoup(html_doc, features="html5lib")
        except Exception as e:
            logger.error("Couldn't parse html document, error: {}".format(e))
            raise e

        return soup

    def get_data(self, soup):
        car_data_dict = {}
        if soup:
            # Find elements using tag name
            titles = soup.find("span", attrs={'class': "title"})
            subtitles = soup.find("span", attrs={'class': "subtitle"})
            prices = soup.find("div", attrs={'class': "price"})
            year = soup.find("span", attrs={'class': "val"})
            mileage = soup.find("dd", attrs={'id': "more_details_kilometers"})

            car_data_dict['title'] = titles.text.strip()
            car_data_dict['subtitle'] = subtitles.text.strip()
            if prices:
                car_data_dict['price'] = prices.text.strip()
            car_data_dict['year'] = year.text.strip()
            if mileage:
                car_data_dict['mileage'] = mileage.text.strip()
            return car_data_dict
        else:
            logger.error("It seems none could be parsed from data tables")
            sys.exit(1)

    def get_id(self, soup):
        return soup.select_one('div', attrs={'class': 'feed_item'}).get('item-id')

    def get_index_records(self, url) -> list:
        logger.info("Fetching records from index page")

        elements = self.html_manager.download_elements(url)
        logger.info("Fetched {} elements from index page".format(len(elements)))

        data_rows = []
        for element in elements:
            soup = self.get_soup(element)
            # data_rows.append(self.get_data(soup))
            data_rows.append(soup)

        return data_rows

    def get_currency_name(self, dataStr):
        for symbol in currencySymbols:
            if symbol in dataStr:
                return currencyMapData.get(symbol)

        return "N/A"

    def getCarID(url):
        propertyID = None

        if url:
            propertyIDResult = propertyIdMatcher.search(url)
            if propertyIDResult:
                propertyID = propertyIDResult.group('propertyID')

        return propertyID

    def product_category(self, url):
        category = None
        result = None

        if url:
            result = pageNameFinder.search(url)
            if result:
                category = result.group(1)

        return category_map.get(category)

    def getCurrentTime(self):
        currentTime = time.time()

        timeStamp = datetime.fromtimestamp(currentTime).strftime('%Y-%m-%d-%H:%M:%S')
        return timeStamp

    def get_record_details(self, record, delay_interval, useProxy) -> dict:
        details_result = {}
        # scrapedData = None

        details_result['id'] = self.get_id(record)
        if not details_result['id']:
            return None

        details_result['detailsLink'] = rootUrl + "/item/" + details_result['id']

        main_scraped_data = {}
        secondary_scraped_data = {}
        details_page = self.car_details_parser.download_html(details_result['detailsLink'], By.TAG_NAME, "body",
                                                             delay_interval, useProxy)
        if details_page:
            soup = self.get_soup(details_page)
            main_scraped_data = self.car_details_parser.parse_main_content(soup)
            secondary_scraped_data = self.car_details_parser.parse_secondary_content(soup)

        details_result['scrapped_on'] = self.getCurrentTime()
        details_result.update(main_scraped_data)
        details_result.update(secondary_scraped_data)

        return details_result

    def get_one_row_data(self, url, row, counter, product_category, delayInterval, useProxy):
        row_details = None

        if product_category == "Cars":
            row_details = self.get_record_details(row, delayInterval, useProxy)

        # print(row_details)
        if row_details:
            row_details['targetUrl'] = url
            row_details['product_category'] = product_category

            self.data_queue.put(row_details)

    def scrap_url_data(self, url, use_proxy, delay_interval):
        data = self.get_index_records(url)
        category = self.product_category(url)

        for data_item in data:
            self.get_one_row_data(url=url, row=data_item, counter=1, product_category=category,
                                  delayInterval=delay_interval, useProxy=use_proxy)

        return self.data_queue


class Yad2IndexParserSimple(Yad2IndexParser):
    def __init__(self, html_manager):
        super(Yad2IndexParserSimple, self).__init__(html_manager=html_manager)

    def get_index_records(self, url) -> list:
        logger.info("Fetching records from index page")

        elements = self.html_manager.download_elements(url)
        logger.info("Fetched {} elements from index page".format(len(elements)))

        data_rows = []
        for element in elements:
            soup = self.get_soup(element)
            data_rows.append(soup)

        return data_rows

    def get_record_details(self, record, delay_interval, useProxy) -> dict:
        details_result = {}

        details_result['id'] = self.get_id(record)
        if not details_result['id']:
            return None

        details_result['detailsLink'] = rootUrl + "/item/" + details_result['id']

        data = self.get_data(record)

        details_result['scrapped_on'] = self.getCurrentTime()
        details_result.update(data)

        return details_result