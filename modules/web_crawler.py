from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from fake_useragent import UserAgent
import asyncio
from pyppeteer import launch
import time


class WebCrawler:
    def __int__(self):
        pass

    def get_elements(self):
        raise NotImplementedError
        pass


def fill_credentials(driver, user_field, password_field, user, pw):
    # Clear any existing content in the field (optional)
    user_field.clear()
    time.sleep(1)
    password_field.clear()
    time.sleep(1)

    # Click the password field to focus on it
    ActionChains(driver).click(user_field).perform()

    for char in user:
        ActionChains(driver).send_keys(char).perform()
        time.sleep(0.2)  # Adjust the delay time as desired

    # Click the password field to focus on it
    ActionChains(driver).click(password_field).perform()

    for char in pw:
        ActionChains(driver).send_keys(char).perform()
        time.sleep(0.2)  # Adjust the delay time as desired

    time.sleep(1)
    # Submit the form (if needed)
    password_field.send_keys(Keys.RETURN)


class SeleniumYad2Crawler(WebCrawler):
    def __init__(self, user, pw):
        self.user = user
        self.pw = pw
        pass

    def get_elements(self):
        self.get_favorites_car_elements()

    def get_ad(self):
        pass

    def get_favorites_car_elements(self):
        options = Options()
        ua = UserAgent()
        user_agent = ua.random
        print(user_agent)

        options.add_argument(f'--user-agent={user_agent}')
        driver = webdriver.Chrome()  # Or use any other driver (e.g., Firefox)
        driver.get("https://www.yad2.co.il/auth/login?continue=https%3A%2F%2Fwww.yad2.co.il%2F&analytics=Site+organic")

        # Wait until the login elements are present
        wait = WebDriverWait(driver, 30)
        username_field = wait.until(EC.presence_of_element_located((By.ID, "email")))
        password_field = wait.until(EC.presence_of_element_located((By.ID, "password")))

        # Fill in the form
        fill_credentials(driver, username_field, password_field, self.user, self.pw)

        # Wait until the desired class appears
        time.sleep(3)

        driver.get("https://www.yad2.co.il/favorites")

        # Wait until the desired class appears
        wait.until(EC.visibility_of_all_elements_located((By.CLASS_NAME, "favorite_items")))

        # Scrape the desired content
        elements = driver.find_elements(By.CLASS_NAME, "favorite_items")
        return elements


class PuppeteerWebCrawler(WebCrawler):
    def __init__(self):
        pass

    def get_elements(self):
        asyncio.get_event_loop().run_until_complete(self._get_elements())

    async def _get_elements(self):
        browser_obj = await launch({"headless": False})
        url = await browser_obj.newPage()
        await url.goto('https://example.com')
        await url.screenshot({'path': 'example.png'})

        await browser_obj.close()

