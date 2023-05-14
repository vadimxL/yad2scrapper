import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


class CarDetailsParser:
    def __init__(self, logger):
        self._logger = logger

    def download_html(self, url, by_what, name, delay_interval, use_proxy=False):
        element = None
        options = Options()
        # options.add_argument("--headless")
        driver = webdriver.Firefox(options=options)
        driver.maximize_window()

        if delay_interval:
            self._logger.info("[!]. Program is sleeping for {} seconds".format(delay_interval))
            time.sleep(delay_interval)  # seconds

        try:
            driver.get(url)
        except Exception as e:
            self._logger.error("Something went wrong here, {}".format(e))
            return None

        head_text = None
        try:
            WebDriverWait(driver, delay_interval).until(EC.element_to_be_clickable((By.CLASS_NAME, "report")))
            element = driver.find_element(by_what, name)
            element = element.get_attribute("innerHTML")

        except Exception as e:
            self._logger.error("Something went wrong here, {}".format(e))
            try:
                head_text = driver.find_element("class name", "msg-head")
            except Exception as e:
                self._logger.error("Something went wrong here, {}".format(e))
                pass
            if head_text:
                self._logger.info("Message: {}".format(head_text.text))

        finally:
            driver.quit()
            if head_text:
                self._logger.info("Message: {}".format(head_text.text))

        return element

    def parse_main_content(self, soup):
        car_data_dict = {}
        title = soup.find("span", attrs={'class': "main_title"})
        second_title = soup.find("span", attrs={'class': "second_title"})
        price = soup.find("strong", attrs={'class': "price"})
        year = soup.find("dd", attrs={'class': "value"})
        # mileage = soup.find("dd", attrs={'id': "more_details_kilometers"})

        car_data_dict['title'] = title.text.strip()
        car_data_dict['subtitle'] = second_title.text.strip()
        if price:
            car_data_dict['price'] = price.text.strip()
        car_data_dict['year'] = year.text.strip()
        # if mileage:
        #     car_data_dict['mileage'] = mileage.text.strip()

        return car_data_dict

    def parse_secondary_content(self, soup):
        car_data_dict = {}
        mileage = soup.find("dd", attrs={'id': "more_details_kilometers"})

        if mileage:
            mileage_string = mileage.text.strip()
            # Remove the comma from the string
            mileage_string = mileage_string.replace(',', '')
            # Convert the string to an integer
            car_data_dict['mileage'] = int(mileage_string)

        return car_data_dict
