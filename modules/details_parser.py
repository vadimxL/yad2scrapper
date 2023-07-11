class CarDetailsParser:
    def __init__(self, logger):
        self._logger = logger

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
        self._logger.info("Parsed main content: {}".format(car_data_dict))
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

        self._logger.info("Parsed secondary content: {}".format(car_data_dict))
        return car_data_dict
