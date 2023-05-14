import unittest

from scrapper.modules.render_html import get_proxy_list, load_proxies_from_file


class MyTestCase(unittest.TestCase):
    def test_something(self):
        self.assertEqual(True, False)  # add assertion here

    def test_get_proxies_list(self):
        print(get_proxy_list())
        print(load_proxies_from_file('./db/proxies.txt'))

if __name__ == '__main__':
    unittest.main()
