#! /usr/bin/env python3
# -*- coding: utf-8 -*-
from pymongo import MongoClient

from modules.index_parser import *
from modules.render_html import FileHtmlManager, SimpleHtmlManager
from modules.report_maker import *
from argparse import ArgumentParser
from datetime import datetime
import os
import time
import re
from selenium.webdriver.remote.remote_connection import LOGGER

from modules.send_mail import send_email

LOGGER.setLevel(logging.WARNING)
LOG_FILENAME = 'webScrapper.log'
# format = '%(asctime)s %(name)-15s %(levelname)-8s %(processName)-10s[%(process)d]%(funcName)10s: %(message)s'
web_scrapper_format = '%(timestamp)s  %(name)s  %(level)s  %(module)s  %(lineno)s  %(message)s'
logging.basicConfig(filename=LOG_FILENAME, format=web_scrapper_format, level=logging.DEBUG)
# logging.basicConfig(format=format, level=logging.DEBUG)
logger = logging.getLogger('webScrapper')

urlMatcher = re.compile(r'https?://[^/]+')
ts = time.time()
timeStamp = datetime.fromtimestamp(ts).strftime('%Y-%m-%d-%H:%M:%S')


def validateUrl(url):
    if urlMatcher.search(url):
        return True
    return False


def main_loop(collection, start_page_num, end_page_num, input_url, useProxy, delayInterval, outFile):
    output_data = None
    isFirstPage = True
    exceptionCount = 0

    # initialize output directories
    initDirs()

    # raw_target_url = "https://www.yad2.co.il/vehicles/cars?carFamilyType=10,5&year=2020-2023&price=0-150000&km=0-40000&hand=0-1&ownerID=1&engineval=1400--1&priceOnly=1&imgOnly=1&page={}"
    raw_target_url = "https://www.yad2.co.il/vehicles/cars?carFamilyType=10,5&year=2020-2023&price=0-150000&km=0-40000&hand=0-1&ownerID=1&engineval=1800--1&priceOnly=1&imgOnly=1&page={}"

    html_mgr = SimpleHtmlManager()
    index_parser = Yad2IndexParserSimple(html_mgr)

    exception_ids = []
    if not input_url:
        data_for_db = []
        for pageNum in range(start_page_num, end_page_num + 1):
            target_url = raw_target_url.format(pageNum)
            logger.info("[>]. Scrapping Page {}: {}\n".format(pageNum, target_url))

            try:
                output_data = index_parser.scrap_url_data(target_url, useProxy, delayInterval)

            except Exception as e:
                exceptionCount += 1
                exception_ids.append(pageNum)
                logger.info(e)
                logger.info("[!]. Exception happened at page {}".format(pageNum))
                exit(1)

            logger.info("[!]. Dumping data into output file")
            fieldnames = output_data.queue[0].keys()

            with open(outFile, 'w', newline='') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

                writer.writeheader()
                writer.writerows(list(output_data.queue))

            data_for_db.extend(list(output_data.queue))
        print("Data for db: ", data_for_db)
        print("Size of data_for_db: ", len(data_for_db))
        i = 0
        for item in data_for_db:
            result = collection.insert_one(item)
            # Print the inserted document's _id
            print("Inserted document ID:", result.inserted_id)
            i += 1
            print("Inserted {} documents".format(i))


    elif input_url:
        target_url = input_url
        logger.info("[>]. Scrapping Url: {}\n".format(target_url))

        try:
            output_data = index_parser.scrap_url_data(target_url, useProxy, delayInterval)
        except Exception as e:
            print(e)

        print("[!]. Dumping data into output file")
        dumpDataFile(output_data, -1, outFile=outFile)

    endTime = time.time()
    endTimeStamp = datetime.fromtimestamp(endTime).strftime('%Y-%m-%d-%H:%M:%S')

    if os.path.exists(outFile):
        if input_url:
            send_email([outFile], 1, 1, timeStamp, endTimeStamp)
        else:
            send_email([outFile], start_page_num, end_page_num, timeStamp, endTimeStamp)

    # endTimeStamp = datetime.fromtimestamp(endTime).strftime('%Y-%m-%d-%H:%M:%S')
    logger.info("[!]. Task launched at '{}'\n".format(endTimeStamp))
    logger.info("[!]. Total encountered Exceptions: {}".format(exceptionCount))
    logger.info("[!]. Encountered Exception IDs: {}".format(', '.join(exception_ids)))


def parse_user_args():
    parser = ArgumentParser(description='Scrap data from YAD')
    parser.add_argument('filename', help='output filename')
    parser.add_argument('-u', '--url', dest='inputUrl', help='Provide a custom input URL for scraping')
    parser.add_argument('-s', '--start-page', type=int, dest='sPageNum', default=1,
                        help='Provide the start page number from where you want to start scrapping')
    parser.add_argument('-e', '--end-page', type=int, dest='ePageNum',
                        help='Provide the last page number upto which you want to do scrapping')
    parser.add_argument('-p', '--use-proxy', dest='useProxy', action='store_true',
                        help='Enable proxy support for scrapping. Proxies are picked up from proxies configuration file "./db/proxies.txt"')
    parser.add_argument('-t', '--use-delay', dest='delayInterval', type=int,
                        help='Provide a sleep delay for which program will sleep before launching every HTTP request')
    parser.add_argument('-C', '--cleanup', dest='cleanup', action='store_true',
                        help='Perform a cleanup operation to remove temporary files')
    group = parser.add_mutually_exclusive_group()
    group.add_argument('-r', '--residential', dest='isResidential', action='store_true',
                       help="Start scrapping using default residential URL")
    group.add_argument('-c', '--commercial', dest='isCommercial', action='store_true',
                       help="Start scrapping using default commercial URL")
    group.add_argument('-v', '--vehicle', dest='is_cars', action='store_true',
                       help="Start scrapping using default cas URL")
    args = parser.parse_args()
    return args


def validate_user_args(args):
    filename = args.filename
    sPageNum = args.sPageNum
    ePageNum = args.ePageNum
    useProxy = args.useProxy
    delayInterval = args.delayInterval
    input_url = args.inputUrl
    isResidential = args.isResidential
    isCommercial = args.isCommercial
    is_cars = args.is_cars

    if (not input_url) and (not (isCommercial or isResidential or is_cars)):
        logger.info("[!]. Please provide scrapping type either -r or -c or -v\n")
        exit(1)

    if input_url:
        input_url = input_url.strip()
        if not validateUrl(input_url):
            logger.info("[ERROR]. URL pattern doesn't seem right")
            exit(1)

    if not input_url:
        if sPageNum and (not ePageNum):
            print("[!]. End page number is not mentioned so only starting page number will be scrapped\n")
            ePageNum = sPageNum

        if sPageNum > ePageNum:
            print("[ERROR]. Start page number should be lesser than ending page number\n")
            exit(1)

        if ePageNum and (not sPageNum):
            print("[!]. Please provide start page number as well\n")
            exit(1)
    elif input_url:
        print("[!]. Start and End page ranges are ignored in case of custom URL\n")
    if useProxy:
        print("[>]. Firefox proxy profile enabled\n")

    if delayInterval:
        print("[>]. Configured a {} seconds delay for each HTTP request\n".format(delayInterval))

    outFile = "{}-{}.csv".format(filename, timeStamp)
    print("[!]. Task launched at '{}'".format(timeStamp))
    return outFile, input_url, sPageNum, ePageNum, useProxy, delayInterval


def setup_db():
    # Connect to MongoDB
    client = MongoClient("mongodb://localhost:27018")
    client.drop_database("yad")
    db = client["yad"]
    collection = db["yad_data"]
    return collection


if __name__ == '__main__':
    args = parse_user_args()
    collection = setup_db()
    outFile, input_url, sPageNum, ePageNum, useProxy, delayInterval = validate_user_args(args)
    while True:
        main_loop(collection, sPageNum, ePageNum, input_url, useProxy, delayInterval, outFile)
        time.sleep(60 * 5)
        print("Sleeping for 5 minutes")
