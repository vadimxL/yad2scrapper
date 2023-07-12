# -*- coding: utf-8 -*-
import pickle
import logging
import time
from fake_useragent import UserAgent
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from modules.proxy_manager import Yad2ProxyManager

# from scrapper.modules.proxy_manager import Yad2ProxyManager

LOG_FILENAME = 'webScrapper.log'
format = '%(asctime)s %(name)-15s %(levelname)-8s %(processName)-10s[%(process)d]%(funcName)10s: %(message)s'
logging.basicConfig(filename=LOG_FILENAME, format=format, level=logging.DEBUG)
# logging.basicConfig(format=format, level=logging.DEBUG)
logger = logging.getLogger('htmlRenderer')


proxiesFile = "./db/proxies.txt"


class HtmlManager:
    def __int__(self, use_proxy=False):
        self.proxy_manager = Yad2ProxyManager(file_name=proxiesFile, logger=logger)
        self.use_proxy = use_proxy

    def generate_random_user_agent(self):
        ua = UserAgent()
        user_agent = ua.random
        return user_agent

    def download_elements(self, url, delay_interval, use_proxy=False):
        elements = []
        options = Options()
        options.add_argument("user-agent={}".format(self.generate_random_user_agent()))

        # options.add_argument("--headless")
        # Set the proxy server in ChromeOptions

        if use_proxy:
            proxy_host, proxy_port = self.proxy_manager.get_proxy()
            options.add_argument("--proxy-server=http://{}:{}".format(proxy_host, proxy_port))
            if proxy_host and proxy_port:
                logger.info("[>]. Firefox proxy profile enabled for proxy:{}:{}".format(proxy_host, proxy_port))
                driver = webdriver.Firefox(options=options)
            else:
                logger.info(
                    "Something is wrong with proxy Host or Port where Host:{} and Port:{}".format(proxy_host,
                                                                                                  proxy_port))
                return
        else:
            driver = webdriver.Firefox(options=options)

        driver.maximize_window()
        if delay_interval:
            logger.info("[!]. Program is sleeping for {} seconds".format(delay_interval))
            time.sleep(delay_interval)

        try:
            driver.get(url)
        except Exception as e:
            logger.error("Something went wrong here, {}".format(e))
            return None

        head_text = None
        try:
            # element = WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.CLASS_NAME, classTag)))
            css_selector = "div.feeditem"
            WebDriverWait(driver, 90).until(EC.element_to_be_clickable((By.CSS_SELECTOR, css_selector)))
            expandables = driver.find_elements(By.CSS_SELECTOR, css_selector)

            elements = []
            for item in expandables:
                item.click()
                inner_html = item.get_attribute("innerHTML")
                elements.append(inner_html)

        except Exception as e:
            logger.error("Something went wrong here, {}".format(e))
            try:
                head_text = driver.find_element("class name", "msg-head")
            except Exception as e:
                logger.error("Something went wrong here, {}".format(e))
                pass
            if head_text:
                logger.info("Message: {}".format(head_text.text))

        finally:
            driver.quit()
            if head_text:
                logger.info("Message: {}".format(head_text.text))

        return elements

    def write_file(self, fname, data):
        try:
            with open(fname, 'wb') as f:
                f.write(data)
                logger.info("File generated successfully")
        except Exception as e:
            raise e


class SimpleHtmlManager:
    def __int__(self, use_proxy=False):
        super(SimpleHtmlManager, self).__init__(use_proxy=use_proxy)

    def download_elements(self, url, delay_interval=False, use_proxy=False):
        elements = []
        options = Options()
        # options.add_argument("--headless")
        # Set the proxy server in ChromeOptions
        driver = webdriver.Firefox(options=options)
        driver.maximize_window()

        try:
            driver.get(url)
        except Exception as e:
            logger.error("Something went wrong here, {}".format(e))
            return None

        head_text = None
        try:
            WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.CLASS_NAME, "feed_list")))
            feed_list = driver.find_element(By.CLASS_NAME, "feed_list")
            items = feed_list.find_elements(By.CSS_SELECTOR, "div.feeditem")

            elements = []
            for item in items:
                # item.click()
                inner_html = item.get_attribute("innerHTML")
                elements.append(inner_html)

        except Exception as e:
            logger.error("Something went wrong here, {}".format(e))
            try:
                head_text = driver.find_element("class name", "msg-head")
            except Exception as e:
                logger.error("Something went wrong here, {}".format(e))
                pass
            if head_text:
                logger.info("Message: {}".format(head_text.text))

        finally:
            driver.quit()
            if head_text:
                logger.info("Message: {}".format(head_text.text))

        return elements


class FileHtmlManager(HtmlManager):
    def __int__(self, use_proxy=False):
        super(FileHtmlManager, self).__init__(use_proxy=use_proxy)

    def download_elements(self, url, delay_interval=False, use_proxy=False):
        # Load the list using pickle
        elements = []
        with open('list.pickle', 'rb') as file:
            elements = pickle.load(file)

        return elements


class CarDetailsHtmlManager(HtmlManager):
    def __int__(self, use_proxy=False):
        super(CarDetailsHtmlManager, self).__init__(use_proxy=use_proxy)

    def download_html(self, url, by_what, name, delay_interval, use_proxy=False):
        element = None
        options = Options()
        # options.add_argument("--headless")
        driver = webdriver.Firefox(options=options)
        driver.maximize_window()

        if delay_interval:
            logger.info("[!]. Program is sleeping for {} seconds".format(delay_interval))
            time.sleep(delay_interval)  # seconds

        try:
            driver.get(url)
        except Exception as e:
            time.error("Something went wrong here, {}".format(e))
            return None

        head_text = None
        try:
            WebDriverWait(driver, delay_interval).until(EC.element_to_be_clickable((By.CLASS_NAME, "report")))
            element = driver.find_element(by_what, name)
            element = element.get_attribute("innerHTML")

        except Exception as e:
            logger.error("Something went wrong here, {}".format(e))
            try:
                head_text = driver.find_element("class name", "msg-head")
            except Exception as e:
                logger.error("Something went wrong here, {}".format(e))
                pass
            if head_text:
                logger.info("Message: {}".format(head_text.text))

        finally:
            driver.quit()
            if head_text:
                logger.info("Message: {}".format(head_text.text))

        return element
