import os
from random import random

import requests
from bs4 import BeautifulSoup


class Yad2ProxyManager:
    def __init__(self, file_name, logger):
        self.fname = file_name
        self._logger = logger

    def get_proxy_list(self):
        url = 'https://free-proxy-list.net/'  # Replace with the URL of the proxy list source
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')

        proxy_list = []
        table = soup.find('table')
        rows = table.find_all('tr')

        for row in rows[1:]:  # Skip the header row
            columns = row.find_all('td')
            ip = columns[0].text.strip()
            port = columns[1].text.strip()
            proxy = f'{ip}:{port}'
            proxy_list.append(proxy)

        if not proxy_list:
            print("[ERROR]: No proxies found")
            exit(1)

        return proxy_list

    def load_proxies_from_file(self):
        try:
            if not os.path.exists(self.fname):
                print("[ERROR]: Proxies file './db/proxies.txt' seems to be missing")
                exit(1)

            with open(self.fname, 'r') as f:
                proxies = f.readlines()

            proxies = [line.strip() for line in proxies]

            if not proxies:
                print("Warning: Proxies file './db/proxies.txt' seems to be empty")
            return proxies
        except Exception as e:
            self._logger.warning(f"Exception excepted during loading proxies from file: {e}")

    def get_proxy(self):
        proxies = self.get_proxy_list()
        chosen_proxy = random.choice(proxies)
        print("Chosen Proxy: {}".format(chosen_proxy))
        proxy_host, proxy_port = chosen_proxy.split(":")

        return (proxy_host, int(proxy_port))

    def prep_proxy_profile(proxy_host, proxy_port):
        profile = webdriver.FirefoxProfile()
        profile.set_preference("network.proxy.type", 1)
        profile.set_preference("network.proxy.http", proxy_host)
        profile.set_preference("network.proxy.http_port", proxy_port)
        profile.set_preference("network.proxy.ssl", proxy_host)
        profile.set_preference("network.proxy.ssl_port", proxy_port)
        profile.update_preferences()

        return profile