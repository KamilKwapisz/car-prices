import unittest
import os.path
import csv
from bs4 import BeautifulSoup
import requests
import sys
sys.path.append('..')

from car_spider import CarSpider
from car_ad_parser import CarParser


class CarParserTestCase(unittest.TestCase):

    def setUp(self):
        self.filename = 'test_cars.csv'
        self.car_parser = CarParser(self.filename)

    def test_plain_text(self):
        text: str = "    tEst plAIn text   "
        right_text: str = "test_plain_text"
        parsed = CarParser.plain_text(text)
        self.assertEqual(parsed, right_text)
        self.assertTrue(parsed.islower())

    def test_file_handling(self):
        self.assertTrue(os.path.isfile(self.filename), "checking if file was created")

        self.car_parser.close_file()
        self.assertTrue(os.path.isfile(self.filename), "checking if file still exists after closing it")

        test_file = open('test_cars.csv', "w")
        self.assertIsNotNone(test_file, "checking if file is closed after executing close_file method")
        test_file.close()

    def test_translate_dict_keys(self):
        invalid_dict: dict = {'test': 'testcase'}
        with self.assertRaises(KeyError):
            CarParser.translate_dict_keys(invalid_dict)

        keys_list = ['make', 'model', 'year', 'mileage', 'petrol_type', 'type', 'no_accidents']
        valid_dict1 = {
            'marka_pojazdu': "bmw",
            'model_pojazdu': "thalia",
            'rok_produkcji': "1998",
            'przebieg': "123_456_km",
            'rodzaj_paliwa': "diesel",
            'typ': "sedan",
            'bezwypadkowy': "tak"
        }

        translated_dict = CarParser.translate_dict_keys(valid_dict1)
        self.assertListEqual(list(translated_dict.keys()), keys_list)
        self.assertEqual(translated_dict['make'], "bmw")
        self.assertEqual(translated_dict['model'], "thalia")
        self.assertEqual(translated_dict['year'], "1998")
        self.assertEqual(translated_dict['mileage'], "123456")
        self.assertEqual(translated_dict['petrol_type'], "diesel")
        self.assertEqual(translated_dict['type'], "sedan")
        self.assertEqual(translated_dict['no_accidents'], True)

        valid_dict1 = {
            'marka_pojazdu': "bmw",
            'model_pojazdu': "thalia",
            'rok_produkcji': "1998",
            'przebieg': "123456",
            'rodzaj_paliwa': "diesel",
            'typ': "sedan",
        }

        translated_dict = CarParser.translate_dict_keys(valid_dict1)
        self.assertEqual(translated_dict['no_accidents'], False)
        self.assertEqual(translated_dict['petrol_type'], "diesel")

        valid_dict2 = {
            'marka_pojazdu': "bmw",
            'model_pojazdu': "thalia",
            'rok_produkcji': "1998",
            'przebieg': "123456",
            'rodzaj_paliwa': "diesel",
            'typ': "sedan",
            'bezwypadkowy': "nie"
        }

        translated_dict = CarParser.translate_dict_keys(valid_dict2)
        self.assertEqual(translated_dict['no_accidents'], False)

    def test_save_data_into_csv_file(self):
        car_details = {
            'make': "renault",
            'model': "thalia",
            'year': "2003",
            'mileage': "123456",
            'petrol_type': "benzyna",
            'type': "sedan",
            'no_accidents': 'True'
        }
        dict_values = list(car_details.values())
        self.car_parser.save_data_into_csv_file(car_details)
        self.car_parser.close_file()

        with open(self.filename, "r") as csvfile:
            read_csv = csv.reader(csvfile, delimiter=',')

            counter = 0
            for row in read_csv:
                self.assertListEqual(dict_values, row)
                counter += 1

            self.assertEqual(counter, 1)

    def test_get_offer_parameters(self):
        with open("offer_params.html") as html_file:
            html = html_file.read()

        soup = BeautifulSoup(html, "html.parser")
        offer_params = CarParser.get_offer_parameters(soup)

        counter = 0
        for param in offer_params:
            self.assertTrue("<li" in str(param))
            self.assertTrue("</li>" in str(param))
            self.assertTrue("""<span class="offer-params__label""" in str(param))
            self.assertTrue("""<div class="offer-params__value""" in str(param))
            counter += 1

        self.assertEqual(counter, 25)

    def test_parse_offer_parameters(self):
        with open("offer_params.html") as html_file:
            html = html_file.read()
        soup = BeautifulSoup(html, "html.parser")
        offer_params = CarParser.get_offer_parameters(soup)
        car_details = CarParser.parse_offer_parameters(offer_params)

        self.assertEqual(car_details['make'], "audi")
        self.assertEqual(car_details['model'], "s3")
        self.assertEqual(car_details['year'], "2014")
        self.assertEqual(car_details['mileage'], "52000")
        self.assertEqual(car_details['petrol_type'], "benzyna")
        self.assertEqual(car_details['type'], "kompakt")
        self.assertTrue(car_details['no_accidents'])

    def test_get_price_and_currency(self):
        html = """
            <div class="offer-price" data-price="130 000">
            <span class="offer-price__number">130 000        <span class="offer-price__currency">PLN</span>
            </span></div>
        """

        soup = BeautifulSoup(html, "html.parser")
        price, currency = CarParser.get_price_and_currency(soup)

        self.assertEqual(type(price), int)
        self.assertEqual(price, 130000)
        self.assertEqual(currency, "PLN")

        price_tag = soup.find('span', {'class': 'offer-price__number'})
        self.assertEqual(price, CarParser.parse_price_tag(price_tag.text), "testing parse_price_tag() method")

    def tearDown(self):
        self.car_parser.close_file()


class CarSpiderTestCase(unittest.TestCase):

    def setUp(self):
        self.starting_page = 'https://www.otomoto.pl/osobowe/volkswagen/golf/?page=1'
        self.limit = 2
        self.spider = car_spider.CarSpider(self.starting_page, self.limit)

    def test_set_car_name(self):
        self.assertEqual(self.spider._car_name, "volkswagen_golf")

    def test_add_links_from_page_to_list(self):
        r = requests.get(self.starting_page)
        self.spider.add_links_from_page_to_list(r)

        self.assertEqual(len(self.spider.car_ads_list), 32)
        for link in self.spider.car_ads_list:
            self.assertTrue("https://www.otomoto.pl/" in link)
            car_name = self.spider._car_name.replace("_", "-")
            self.assertTrue(car_name in link)

    def test_get_car_ads_list(self):
        self.spider.get_car_ads_list()

        self.assertEqual(len(self.spider.car_ads_list), 64)
        self.assertEqual(self.spider._page_number, 3)

    def tearDown(self):
        self.spider.close_csv_file_in_parser()






