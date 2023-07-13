import logging
from collections import namedtuple
from datetime import datetime
import time
from argparse import ArgumentParser
import re
logger = logging.getLogger('webScrapper')


class UserArgsParser:
    def __init__(self):
        self.parser = ArgumentParser(description='Scrap data from YAD')

    def parse_user_args(self):
        parser = self.parser
        parser.add_argument('filename', help='output filename')
        parser.add_argument('-u', '--url', dest='input_url', help='Provide a custom input URL for scraping')
        parser.add_argument('-s', '--start-page', type=int, dest='start_page_num', default=1,
                            help='Provide the start page number from where you want to start scrapping')
        parser.add_argument('-e', '--end-page', type=int, dest='end_page_num',
                            help='Provide the last page number upto which you want to do scrapping')
        parser.add_argument('-p', '--use-proxy', dest='use_proxy', action='store_true',
                            help='Enable proxy support for scrapping. Proxies are picked up from proxies configuration file "./db/proxies.txt"')
        parser.add_argument('-t', '--use-delay', dest='delay_interval', type=int,
                            help='Provide a sleep delay for which program will sleep before launching every HTTP request')
        parser.add_argument('-C', '--cleanup', dest='cleanup', action='store_true',
                            help='Perform a cleanup operation to remove temporary files')
        group = parser.add_mutually_exclusive_group()
        group.add_argument('-r', '--residential', dest='is_residential', action='store_true',
                           help="Start scrapping using default residential URL")
        group.add_argument('-c', '--commercial', dest='is_commercial', action='store_true',
                           help="Start scrapping using default commercial URL")
        group.add_argument('-v', '--vehicle', dest='is_cars', action='store_true',
                           default=True,
                           help="Start scrapping using default cars URL")
        args = parser.parse_args()
        return args

    def validate_url(self, url):
        url_matcher = re.compile(r'https?://[^/]+')
        if url_matcher.search(url):
            return True
        return False

    def validate_user_args(self, arguments):
        filename = arguments.filename
        s_page_num = arguments.start_page_num
        e_page_num = arguments.end_page_num
        use_proxy = arguments.use_proxy
        delay_interval = arguments.delay_interval
        input_url = arguments.input_url
        is_residential = arguments.is_residential
        is_commercial = arguments.is_commercial
        is_cars = arguments.is_cars

        if not input_url and not (is_commercial or is_residential or is_cars):
            logger.info("[!]. Please provide scraping type either -r or -c or -v\n")
            exit(1)

        if input_url:
            input_url = input_url.strip()
            if not self.validate_url(input_url):
                logger.info("[ERROR]. URL pattern doesn't seem right")
                exit(1)

        if not input_url:
            if s_page_num and not e_page_num:
                print("[!]. End page number is not mentioned, so only the starting page number will be scrapped\n")
                e_page_num = s_page_num

            if s_page_num > e_page_num:
                print("[ERROR]. Start page number should be lesser than the ending page number\n")
                exit(1)

            if e_page_num and not s_page_num:
                print("[!]. Please provide a start page number as well\n")
                exit(1)
        elif input_url:
            print("[!]. Start and End page ranges are ignored in case of a custom URL\n")

        if use_proxy:
            print("[>]. Firefox proxy profile enabled\n")

        if delay_interval:
            print("[>]. Configured a {} seconds delay for each HTTP request\n".format(delay_interval))

        if is_cars and not input_url:
            input_url = 'https://www.yad2.co.il/vehicles/cars?'

        ts = time.time()
        timestamp = datetime.fromtimestamp(ts).strftime('%Y-%m-%d-%H:%M:%S')
        out_file = "{}-{}.csv".format(filename, timestamp)
        print("[!]. Task launched at '{}'".format(timestamp))
        Args = namedtuple('Args', ['out_file', 'input_url', 's_page_num', 'e_page_num', 'use_proxy', 'delay_interval'])
        return Args(out_file, input_url, s_page_num, e_page_num, use_proxy, delay_interval)
