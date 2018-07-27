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

    def test_
