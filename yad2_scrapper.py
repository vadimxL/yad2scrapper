import csv
import os
import re
import time
from datetime import datetime
import logging
from modules.index_parser import Yad2IndexParserSimple
from modules.render_html import SimpleHtmlManager, FileHtmlManager
from modules.report_maker import initDirs, dumpDataFile
from modules.send_mail import send_email

logger = logging.getLogger('yad2_scrapper')


class Yad2Scrapper:
    def __init__(self, timestamp, db):
        self.timestamp = timestamp
        self.db = db

    def main_loop(self, args):
        start_page_num = args.s_page_num
        end_page_num = args.e_page_num
        input_url = args.input_url
        use_proxy = args.use_proxy
        delay_interval = args.delay_interval
        out_file = args.out_file
        exceptionCount = 0

        # initialize output directories
        initDirs()

        raw_target_url = self.build_yad2_url(start_page_num, input_url)
        html_mgr = SimpleHtmlManager(is_quiet=True)
        # html_mgr = FileHtmlManager()
        index_parser = Yad2IndexParserSimple(html_mgr)

        exception_ids = []
        data_for_db = []
        for pageNum in range(start_page_num, end_page_num + 1):
            target_url = raw_target_url.format(pageNum)
            logger.info("[>]. Scrapping Page {}: {}\n".format(pageNum, target_url))

            try:
                output_data = index_parser.scrap_url_data(target_url, use_proxy, delay_interval)

            except Exception as e:
                exceptionCount += 1
                exception_ids.append(pageNum)
                logger.info("[!]. Exception {} happened at page {}".format(e, pageNum))
                exit(1)

            data_for_db.extend(list(output_data.queue))

        self.save_to_db(data_for_db, self.timestamp)
        price_changes = self.get_price_changes()

        if price_changes is None:
            logger.info("[!]. No price changes found")
            return

        logger.info("[!]. Dumping price changes into output file")
        with open(out_file, "w") as f:
            f.write(price_changes)

        end_time_stamp = datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d-%H:%M:%S')

        if os.path.exists(out_file):
            send_email([out_file], 1, 1, self.timestamp, end_time_stamp)

        # end_time_stamp = datetime.fromtimestamp(endTime).strftime('%Y-%m-%d-%H:%M:%S')
        logger.info("[!]. Task launched at '{}'\n".format(end_time_stamp))
        logger.info("[!]. Total encountered Exceptions: {}".format(exceptionCount))
        logger.info("[!]. Encountered Exception IDs: {}".format(', '.join(exception_ids)))

    def build_yad2_url(self, page_number, base_url):
        car_family_type = "carFamilyType=10,5"
        year = "year=2020-2023"
        price = "price=0-150000"
        km = "km=0-40000"
        hand = "hand=0-1"
        owner_id = "ownerID=1"
        engine_val = "engineval=1800--1"
        price_only = "priceOnly=1"
        img_only = "imgOnly=1"
        page = f"page={page_number}"

        url = f"{base_url}{car_family_type}&{year}&{price}&{km}&{hand}&{owner_id}&{engine_val}&{price_only}&{img_only}&{page}"
        return url

    def save_to_db(self, data_for_db, timestamp):
        for item in data_for_db:
            self.update_and_track_history(item, timestamp)
            # result = self.collection.update_one({'_id': item['_id']}, {'$set': item}, upsert=True)

    def update_and_track_history(self, item, timestamp):
        # Update the fields and push the changes to history arrays
        if 'price' not in item:
            item['price'] = 'no_price'
        self.db.update_one(
            {'_id': item['id']},
            {
                '$set': item,
                '$push': {
                    'priceHistory': {'timestamp': timestamp, 'value': item['price']},
                }
            },
            upsert=True
        )

    def get_price_changes(self):
        price_changes = "title, id, current price, previous price, timestamp\n"
        for item in self.db.find():
            # Extract the car make and model
            car_make_model = item['title']

            # Extract the price history data
            price_history = item['priceHistory']
            num_entries = len(price_history)

            if num_entries < 2:
                continue  # Skip if there's only one price history entry

            price_changes += f"{car_make_model}, id={item['_id']}, "

            # Extract the last two entries
            last_two_entries = price_history[-2:]

            # Extract the prices and timestamps
            current_price = float(re.sub(r'[^\d.]', '', last_two_entries[1]['value']))
            previous_price = float(re.sub(r'[^\d.]', '', last_two_entries[0]['value']))
            current_timestamp = last_two_entries[1]['timestamp']

            # Check if the price changed
            if current_price != previous_price:
                price_changes += f"{previous_price:.2f}, {current_price:.2f}, {current_timestamp}"
                price_changes += "\n"
            else:
                return None

        return price_changes

