import csv
import datetime
import json
import locale
import re
from bs4 import BeautifulSoup
import glob
import os
from datetime import datetime, timedelta
import matplotlib.pyplot as plt

from pymongo import MongoClient

from modules.web_crawler import SeleniumYad2Crawler, PuppeteerWebCrawler


def setup_favorites_db():
    # Connect to MongoDB
    client = MongoClient("mongodb://localhost:27018")
    client.drop_database("favorites_yad2")
    db = client["favorites_yad2"]
    collection = db["favorites_yad2data"]
    return collection


def save_to_json(out_name, car_listings_sorted):
    # Save the sorted car listings to a JSON file
    with open(out_name + ".csv", 'w') as f:
        json.dump(car_listings_sorted, f, indent=4, ensure_ascii=False)


def save_to_csv(out_name, car_listings_sorted):
    filename = out_name + ".csv"
    # Save the sorted car listings to a CSV file
    with open(filename, mode="w", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=car_listings_sorted[0].keys())

        # Write the header row
        writer.writeheader()

        for listing in car_listings_sorted:
            writer.writerow(listing)  # Write each car listing as a row

    # print(f"Car listing saved to {filename} successfully.")


def saved_recently(current_directory):
    minutes = 30
    # folder_name = 'folder'  # Replace with the actual folder name
    current_time = datetime.now()
    time_threshold = timedelta(minutes=minutes)

    # Create the folder path relative to the current directory
    # folder_path = os.path.join(current_directory, folder_name)
    latest_file_path = None
    latest_file_time = datetime.min

    # Iterate over files in the folder
    for file_name in os.listdir(current_directory):
        file_path = os.path.join(current_directory, file_name)
        if os.path.isfile(file_path) and file_name.endswith('.html') and file_name.startswith('scraped'):
            # Extract the timestamp from the file name
            timestamp_str = file_name.split('_')[-1].split('.')[0]
            timestamp_year_month_day_str = file_name.split('_')[-2].split('.')[0]
            timestamp_str = timestamp_year_month_day_str + '-' + timestamp_str
            file_time = datetime.strptime(timestamp_str, "%Y-%m-%d-%H-%M")

            # Check if the file time is later than the previous latest file
            if file_time > latest_file_time:
                latest_file_path = file_path
                latest_file_time = file_time

    # Check if the latest file exists and if more than 5 minutes have passed
    if latest_file_path is not None:
        time_diff = current_time - latest_file_time
        if time_diff > time_threshold:
            print(f"More than {minutes} minutes have passed since the latest .html file was created.")
            return False
        else:
            print(f"Less than or equal to {minutes} minutes have passed since the latest .html file was created.")
            return True
    else:
        print("No .html files found in the folder.")
        return False


def get_html_file_list(new_directory):
    html_files = glob.glob(os.path.join(new_directory, '*.html'))

    # Create a list of file names without the ".html" extension
    html_files_list = [os.path.splitext(os.path.basename(file))[0] for file in html_files]

    # Print the list of HTML file names without the ".html" extension
    return [str(file_name) for file_name in html_files_list]


def get_latest_html_file_without_type(folder_path):
    # Specify the pattern of the filename
    filename_pattern = 'scraped_content_*.html'

    # Get a list of all files matching the pattern in the folder
    html_files = glob.glob(os.path.join(folder_path, filename_pattern))

    # Sort the files by modification time in descending order
    html_files.sort(key=os.path.getmtime, reverse=True)

    # Get the most recent file
    most_recent_file = os.path.splitext(os.path.basename(html_files[0]))[0]

    return most_recent_file


class Yad2FavoritesScraper:
    # driver = webdriver.Chrome()  # Or use any other driver (e.g., Firefox)
    def __init__(self):
        self.username = "malinvadim88@gmail.com"
        self.password = "Alona1990"
        self.collection = setup_favorites_db()
        # self.crawler = SeleniumYad2Crawler(self.username, self.password)
        self.crawler = PuppeteerWebCrawler()

        # Create a new directory path next to the Python binary
        current_directory = os.path.dirname(os.path.abspath(__file__))
        self.html_save_dir = os.path.join(current_directory, "scraped_content")
        self.csv_save_dir = os.path.join(current_directory, "scraped_content_parsed_csv")

        # Create the new directory if it doesn't exist
        if not os.path.exists(self.html_save_dir):
            os.makedirs(self.html_save_dir)

        # Create the new directory if it doesn't exist
        if not os.path.exists(self.csv_save_dir):
            os.makedirs(self.csv_save_dir)

    def run(self):
        file_name = os.path.join(self.html_save_dir,
                                 f"scraped_content_{datetime.now().strftime('%Y-%m-%d_%H-%M')}.html")

        if not saved_recently(self.html_save_dir):
            elements = self.crawler.get_favorites_car_elements()
            self.save_list_of_favorite_cars(elements, file_name)

        # Parse HTML files and save the results to CSV files
        html_files_list = get_html_file_list(self.html_save_dir)
        # html_files_list = get_latest_html_file_without_type(self.html_save_dir)
        if type(html_files_list) is str:
            html_files_list = [html_files_list]
        for name in html_files_list:
            file_name = os.path.join(self.html_save_dir, name + '.html')
            with open(file_name, 'r') as file:
                html_doc = file.read()
                car_listings = self.parse_favorites(html_doc)
                save_to_csv(os.path.join(self.csv_save_dir, name), car_listings)
                # Extract the timestamp substring
                timestamp_string = name.split("_")  # Assuming the timestamp is always the third substring
                timestamp_string = timestamp_string[2] + '_' + timestamp_string[3]
                # Parse the timestamp into a datetime object
                timestamp = datetime.strptime(timestamp_string, "%Y-%m-%d_%H-%M")

                self.save_to_db(car_listings, timestamp)

        # self.plot_price_history()
        self.print_price_changes()

    def save_to_db(self, data_for_db, timestamp):
        for item in data_for_db:
            self.update_and_track_history(item, timestamp)
            # result = self.collection.update_one({'_id': item['_id']}, {'$set': item}, upsert=True)

    def get_mileage(self):
        pass

    def save_list_of_favorite_cars(self, elements, file_name):
        # Open the file in write mode
        with open(file_name, "w", encoding="utf-8") as file:
            # Write the HTML content to the file
            file.write("<html><body>")
            for element in elements:
                file.write(element.get_attribute("outerHTML"))
            file.write("</body></html>")

        print(f"Scraped content saved to {file_name}")

    def parse_favorites(self, html_doc):
        car_listings = []
        seen_ids = set()

        # Set the locale to your desired format
        locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')

        # Create a BeautifulSoup object
        soup = BeautifulSoup(html_doc, 'html.parser')
        # body = soup.body
        category_items = soup.find("div", attrs={'class': "favorite_items"})
        elements = category_items.findAll('li')
        # elements = soup.selectAll('div.favorites_item')
        # Extract car make and model
        for element in elements:
            # Extract car make and model
            make_model_element = element.select_one('span.title')
            car_make_model = make_model_element.text.strip() if make_model_element else "Make and model not found"

            # Extract year, hand, and other information
            year_element = element.select_one('div.data.year-item > span.val')
            year = year_element.text.strip() if year_element else "Year not found"

            hand_element = element.select_one('div.data.hand-item > span.val')
            hand = hand_element.text.strip() if hand_element else "Hand not found"

            engine_size_element = element.select_one('div.data.engine_size-item > span.val')
            engine_size = engine_size_element.text.strip() if engine_size_element else "Engine size not found"

            # Extract price information
            price_element = element.select_one('div.price')
            price_text = price_element.text.strip() if price_element else "Price not found"

            # Find the div element and extract the item-id attribute value
            item_id = "Item ID not found"
            div_element = element.find('div', class_='feed_item-v4')
            if div_element:
                item_id = div_element['item-id']

            # Remove commas from price text
            price_text = price_text.replace(',', '')

            # Extract price in integer format and currency
            price_match = re.search(r'(\d+)', price_text)
            price = int(price_match.group(1)) if price_match else 0

            currency_match = re.search(r'(\D+)', price_text)
            currency = currency_match.group(1) if currency_match else "Currency not found"

            # Format price with thousands separator
            formatted_price = locale.format_string("%d", price, grouping=True)

            # Create a dictionary for the car listing
            car_listing = {
                '_id': item_id,
                'Car Make and Model': car_make_model,
                'Year': year,
                'Hand': hand,
                'Engine Size': engine_size,
                'Price': formatted_price + " " + currency,
                # 'Currency': currency,
                'Link': f"https://www.yad2.co.il/item/{item_id}"
            }

            # self.save_full_info(car_listing['Link'])
            # mileage = self.get_mileage(car_listing['Link'])
            # car_listing['mileage'] = mileage

            # Append the car listing to the list
            if car_listing["_id"] not in seen_ids and car_listing["_id"] != "_id not found":
                car_listings.append(car_listing)
                seen_ids.add(car_listing["_id"])

        # Sort the car listings by price in ascending order
        # self.translate_car_data(car_listings)

        # save_to_json(out_name, car_listings_sorted)
        return car_listings

    def update_and_track_history(self, item, timestamp):
        # Update the fields and push the changes to history arrays
        self.collection.update_one(
            {'_id': item['_id']},
            {
                '$set': item,
                '$push': {
                    'priceHistory': {'timestamp': timestamp, 'value': item['Price']},
                }
            },
            upsert=True
        )

    def plot_price_history(self):
        # Create a new directory for saving the plots
        save_directory = 'path/to/new_directory'
        os.makedirs(save_directory, exist_ok=True)

        # Iterate over the items in the collection
        for item in self.collection.find():
            # Create a new plot for each item
            fig, ax = plt.subplots()

            # Extract the car make and model
            car_make_model = item['Car Make and Model']

            # Extract the price history data
            price_history = item['priceHistory']
            timestamps = []
            prices = []
            for entry in price_history:
                timestamps.append(entry['timestamp'])
                price_string = re.sub(r'[^\d.]', '', entry['value'])  # Remove non-numeric characters
                prices.append(float(price_string))

            # Plot the price history using histogram bins
            ax.hist(prices, bins=10)  # Adjust the number of bins as needed

            ax.set_xlabel('Timestamp')
            ax.set_ylabel('Price')
            ax.set_title(f'Price History - {car_make_model}')

            # Save each plot in the specified directory
            filename = f'{item["_id"].replace(" ", "_")}_price_history.png'
            save_path = os.path.join(save_directory, filename)
            plt.savefig(save_path, dpi=300)

            # Close the current plot to proceed to the next item
            plt.close(fig)

    def print_price_changes(self):
        # Iterate over the items in the collection
        for item in self.collection.find():
            # Extract the car make and model
            car_make_model = item['Car Make and Model']

            # Extract the price history data
            price_history = item['priceHistory']
            previous_price = None

            print(f"Price changes for {car_make_model}, id={item['_id']}:")
            for entry in price_history:
                price_string = re.sub(r'[^\d.]', '', entry['value'])  # Remove non-numeric characters
                current_price = float(price_string)
                timestamp = entry['timestamp']

                if previous_price is not None:
                    price_change = current_price - previous_price
                    if price_change > 0:
                        print(f"Current price: {current_price:.2f}, Timestamp: {timestamp}")
                else:
                    print(f"Current price: {current_price:.2f}, Timestamp: {timestamp}")

                previous_price = current_price

            print()


if __name__ == '__main__':
    Yad2FavoritesScraper().run()
