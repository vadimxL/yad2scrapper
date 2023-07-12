import unittest

from modules.favorites_scraper import Yad2FavoritesScraper, get_latest_html_file_without_type


class MyTestCase(unittest.TestCase):
    favorites_scraper = Yad2FavoritesScraper()

    def test_load_latest_file_from_dir(self):
        html_save_dir = self.favorites_scraper.html_save_dir
        html_files_list = get_latest_html_file_without_type(html_save_dir)
        print(html_files_list)

    def test_puppeteer(self):
        elements = self.favorites_scraper.crawler.get_elements()
        print(elements)


if __name__ == '__main__':
    unittest.main()
