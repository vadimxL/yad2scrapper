import json
import pickle
import unittest
from pathlib import Path

from scrapper.modules.indexParser import YAD2_TABLE_LIST, Yad2IndexParser
from scrapper.modules.render_html import HtmlManager


class Yad2Test(unittest.TestCase):
    def test_parse_html_from_pickled_file(self):
        yad2_index_parser = Yad2IndexParser()
        data_rows = {}

        # Load the list using pickle
        elements = []
        with open('list.pickle', 'rb') as file:
            elements = pickle.load(file)

        for element in elements:
            soup = yad2_index_parser.get_soup(element)
            data = yad2_index_parser.get_data(soup)
            data_rows[data['title']] = data

        file_path = "data.json"
        with open(file_path, "w") as data_file:
            json.dump(data_rows, data_file, indent=4, ensure_ascii=False)

        # Read the file and check its content
        with open(file_path, 'r') as file:
            content = file.read()
            print(content)
            self.assertTrue(content)  # Assert that content is not empty

    def test_parse_html_from_full_page(self):
        html_manager = HtmlManager()
        url = "https://www.yad2.co.il/vehicles/cars?carFamilyType=10,2,9,5,4,3,8&year=2023-2023&price=0-150000&km=0-60000&hand=1-1&ownerID=1&priceOnly=1&imgOnly=1"

        # url = raw_target_url.format(1)
        # print("[>]. Scrapping Page {}: {}\n".format(1, url))

        # elements = html_manager.download_elements(url, delay_interval, use_proxy)
        elements = html_manager.download_elements_from_full_page(url)

        yad2_index_parser = Yad2IndexParser()
        data_rows = {}

        for element in elements:
            soup = yad2_index_parser.get_soup(element)
            data = yad2_index_parser.get_data(soup)
            data_rows[data['title']] = data

        # # Save the list using pickle
        with open('list.pickle', 'wb') as file:
            pickle.dump(elements, file)

        print(data_rows)


if __name__ == '__main__':
    unittest.main()
