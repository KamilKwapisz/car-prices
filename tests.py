import unittest
from car_ad_parser import CarParser
import os.path


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
        with self.assertRaises(KeyError) as key_err:
            translate_dict_keys(invalid_dict)

        the_exception = key_err.exception
        self.assertEqual(str(the_exception), "Offer does not contain crucial information")

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

        translated_dict = CarParser.translate_dict_keys(valid_dict1)
        self.assertEqual(translated_dict['no_accidents'], False)





