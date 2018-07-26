import requests  # temporarily
from bs4 import BeautifulSoup
import csv


class CarParser(object):

    def __init__(self, filename='cars.csv'):
        self._file = open(filename, "a", newline='')

    def save_car_details_from_ad_page(self, url: str):
        r = requests.get(url)
        soup = BeautifulSoup(r.text, "html.parser")

        offer_parameters = CarParser.get_offer_parameters(soup)
        price, currency = CarParser.get_price_and_currency(soup)

        car_details = CarParser.parse_offer_parameters(offer_parameters)
        car_details['price'] = price
        car_details['currency'] = currency

        self.save_data_into_csv_file(car_details)

    @staticmethod
    def get_offer_parameters(soup):
        div_with_offer_param = soup.find('div', class_="offer-params")
        offer_params = div_with_offer_param.find_all('li', {'class': 'offer-params__item'})
        return offer_params

    @staticmethod
    def get_price_and_currency(soup):
        price_tag = soup.find('span', {'class': 'offer-price__number'})
        price = CarParser.parse_price_tag(price_tag.text)
        currency = price_tag.find('span', {'class': 'offer-price__currency'}).text

        return price, currency

    @staticmethod
    def parse_price_tag(price_tag: str) -> int:
        price_tag = price_tag.replace(' ', '')
        price_list = []
        for ch in price_tag:
            if ch.isdigit():
                price_list.append(ch)

        price = int("".join(price_list))
        return price

    @staticmethod
    def parse_offer_parameters(offer_parameters) -> dict:
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
        try:
            car_details['make'] = CarParser.plain_text(car_details.pop('marka_pojazdu'))
            car_details['model'] = CarParser.plain_text(car_details.pop('model_pojazdu'))
            car_details['year'] = CarParser.plain_text(car_details.pop('rok_produkcji'))
            car_details['mileage'] = CarParser.plain_text(car_details.pop('przebieg'))[:-3].replace('_', '')
            car_details['petrol_type'] = CarParser.plain_text(car_details.pop('rodzaj_paliwa'))
            car_details['type'] = CarParser.plain_text(car_details.pop('typ'))
        except KeyError:
            # if ad has no such data I assume it's a fake ad
            return dict()

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
        self._file.close()