from bs4 import BeautifulSoup
import requests
from user_agent import generate_user_agent

from .car_ad_parser import CarParser


class CarSpider(object):

    def __init__(self, starting_url: str, pages_limit: int):
        self.starting_url: str = self.parse_url(starting_url)
        self._car_name = None
        self._page_number = 1
        self._pages_limit = pages_limit
        self.set_car_name()
        self.car_ads_list = list()
        self.parser = CarParser('cars.csv')

    def set_car_name(self):
        """
        Method extract car's make and model from starting url and save it with '_' separator eg "volkswagen_golf"
        """
        chunks = self.starting_url.split('/')
        self.car_name = '_'.join(chunks[-3:-1])

    def add_links_from_page_to_list(self, request):
        """
        Method parse HTML code from starting page and extract link to listed offers and fill car_ads_list with them
        :param request: requests get object - request = requests.get(self.starting_url)
        """
        soup = BeautifulSoup(request.text, "html.parser")
        tags = soup('a', {'class': 'offer-title__link'})
        for tag in tags:
            try:
                self.car_ads_list.append(tag.get('href'))
            except Exception:
                continue

    def get_car_ads_list(self):
        """
        Method send get request to a number (pages_limit variable) pages listing car offers and fetch requests object
        which are passed to a add_links_from_page_to_list() method
        """
        base_url: str = self.starting_url[:-1]
        while self._page_number <= self._pages_limit:
            ad_url = base_url + str(self._page_number)
            print("link: ", ad_url)
            user_agent = str(generate_user_agent(os=('mac', 'linux', 'win')))
            r = requests.get(ad_url, headers={'User-agent': user_agent})

            self.add_links_from_page_to_list(r)

            self._page_number += 1
        print("cars list created")

    def crawl(self):
        """
        Method crawl each site in car_ads_list collection
        """
        self.get_car_ads_list()

        if len(self.car_ads_list) > 0:
            for link in self.car_ads_list:
                self.parser.save_car_details_from_ad_page(link)
        else:
            print("You need to call method 'add_links_from_page_to_list' to collect list of links to crawl.")
        self.parser.close_file()

    @property
    def car_name(self):
        return self._car_name

    @car_name.setter
    def car_name(self, value):
        self._car_name = value

    @car_name.deleter
    def car_name(self):
        del self._car_name

    def close_csv_file_in_parser(self):
        self.parser.close_file()

    @staticmethod
    def parse_url(car_type_url: str) -> str:
        try:
            question_mark_index = car_type_url.index('?')
            valid_url = car_type_url[:question_mark_index+1] + "page=1"
            return valid_url
        except ValueError:
            return car_type_url + "?page=1"

# for url in url_list:
#     spider = CarSpider(url, 5)
#     spider.crawl()
