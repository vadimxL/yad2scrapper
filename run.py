#! /usr/bin/env python3
# -*- coding: utf-8 -*-
from pymongo import MongoClient
from datetime import datetime
import time
from modules.report_maker import *
from selenium.webdriver.remote.remote_connection import LOGGER
from user_arguments_parser import UserArgsParser
from yad2_scrapper import Yad2Scrapper

LOGGER.setLevel(logging.WARNING)
LOG_FILENAME = 'webScrapper.log'
web_scrapper_format = '%(timestamp)s  %(name)s  %(level)s  %(module)s  %(lineno)s  %(message)s'
logging.basicConfig(filename=LOG_FILENAME, format=web_scrapper_format, level=logging.DEBUG)
logger = logging.getLogger('webScrapper')


def setup_db():
    # Connect to MongoDB
    client = MongoClient("mongodb://localhost:27018")
    client.drop_database("yad")
    db = client["yad"]
    return db["yad_data"]


if __name__ == '__main__':
    minutes = 2
    start_timestamp = datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d-%H:%M:%S')
    yad2_scrapper = Yad2Scrapper(start_timestamp, setup_db())
    user_args_parser = UserArgsParser()
    args = user_args_parser.parse_user_args()
    collection = setup_db()
    result = user_args_parser.validate_user_args(args)
    while True:
        yad2_scrapper.main_loop(result)
        time.sleep(60 * minutes)
        print(f"Sleeping for {minutes} minutes")
