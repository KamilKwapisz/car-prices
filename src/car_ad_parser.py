import requests  # temporarily
from bs4 import BeautifulSoup
import csv


class CarParser(object):

    def __init__(self, filename='cars.csv'):
        self._file = open(filename, "a", newline='')

    def save_car_details_from_ad_page(self, url: str):
        """
        Method request given url and control process of parsing car data and saving it into .csv file
        :param url: link to a car advertisement(offer)
        """
        r = requests.get(url)
        soup = BeautifulSoup(r.text, "html.parser")

        try:
            offer_parameters = CarParser.get_offer_parameters(soup)
            price, currency = CarParser.get_price_and_currency(soup)

            car_details = CarParser.parse_offer_parameters(offer_parameters)
            car_details['price'] = price
            car_details['currency'] = currency

            self.save_data_into_csv_file(car_details)
        except (KeyError, AttributeError) as e:
            print(e)

    @staticmethod
    def get_offer_parameters(soup):
        """
        Method parse HTML code in order to get all offer parameters.
        :param soup: BeautifulSoup object created with html from requested offer page
        :return: BeautifulSoup collection of offer parameters
        """
        div_with_offer_param = soup.find('div', class_="offer-params")
        offer_params = div_with_offer_param.find_all('li', {'class': 'offer-params__item'})
        return offer_params

    @staticmethod
    def get_price_and_currency(soup):
        """
        Method parse HTML code to get car price and currency
        :param soup: BeautifulSoup object created with html from requested offer page
        :return: car price(int) and currency(str)
        """
        price_tag = soup.find('span', {'class': 'offer-price__number'})
        price = CarParser.parse_price_tag(price_tag.text)
        currency = price_tag.find('span', {'class': 'offer-price__currency'}).text

        return price, currency

    @staticmethod
    def parse_price_tag(price_tag: str) -> int:
        """
        Method parse tag containing price and currency
        :param price_tag: span with price text and another span with currency
        :return: integer number representing car price
        """
        price_tag = price_tag.replace(' ', '')
        if ',' in price_tag:
            # some ads have price with cents(eg 56 421,21), but we will omit them
            coma_index = price_tag.index(',')
            price_tag = price_tag[:coma_index]

        price_list = []
        for ch in price_tag:
            if ch.isdigit():
                price_list.append(ch)

        price = "".join(price_list)
        return int(price)

    @staticmethod
    def parse_offer_parameters(offer_parameters) -> dict:
        """
        Parse offer parameters from html tags into python dict
        :param offer_parameters: html tags containing car offer parameters
        :return: dict with car offer parameters
        """
        car_details = dict()
        accepted_keys = [
            'marka_pojazdu',
            'model_pojazdu',
            'rok_produkcji',
            'przebieg',
            'rodzaj_paliwa',
            'typ',
            'bezwypadkowy'
        ]
        for param in offer_parameters:
            label = CarParser.plain_text(param.span.text)
            if label in accepted_keys:
                value = CarParser.plain_text(param.div.text)
                car_details[label] = value

        car_details = CarParser.translate_dict_keys(car_details)
        return car_details

    @staticmethod
    def translate_dict_keys(car_details: dict) -> dict:
        """
        Translate car_details dict keys from polish to english
        :param car_details: dict with all car details
        :return: car_details dict with keys in english
        """
        try:
            car_details['make'] = CarParser.plain_text(car_details.pop('marka_pojazdu'))
            car_details['model'] = CarParser.plain_text(car_details.pop('model_pojazdu'))
            car_details['year'] = CarParser.plain_text(car_details.pop('rok_produkcji'))
            car_details['mileage'] = CarParser.plain_text(car_details.pop('przebieg'))[:-3].replace('_', '')
            car_details['petrol_type'] = CarParser.plain_text(car_details.pop('rodzaj_paliwa'))
            car_details['type'] = CarParser.plain_text(car_details.pop('typ'))
        except KeyError:
            # if ad has no such data I assume it's a fake ad
            raise KeyError("Offer does not contain crucial information.")

        # when ad has no information about car having an accident I assume that it had one
        try:
            acc = CarParser.plain_text(car_details.pop('bezwypadkowy'))
            if acc == "tak":
                car_details['no_accidents'] = True
            else:
                car_details['no_accidents'] = False
        except KeyError:
            car_details['no_accidents'] = False

        return car_details

    def save_data_into_csv_file(self, car_details: dict):
        """
        Write car_details dict as a row to a csv file
        :param car_details:
        """
        try:
            fieldnames = list(car_details.keys())

            writer = csv.DictWriter(self._file, fieldnames=fieldnames)
            writer.writerow(car_details)
        except (AttributeError, TypeError, FileNotFoundError) as e:
            print(e)

    @staticmethod
    def plain_text(text: str) -> str:
        return text.strip().replace(" ", "_").lower()

    def close_file(self):
        try:
            self._file.close()
        except IOError:
            pass
