import requests
import logging
# import pandas as pd
import time
import random
import csv
from urllib.request import urlopen
from envyaml import EnvYAML
import json
from itertools import islice
from urllib.error import URLError, HTTPError
from config import mongodb_connector


class CategoriesLinksCrawling:

    def __init__(self):
        self.env = EnvYAML('../config/config.yaml')
        self.api = self.env['api']
        self.menu = self.api['menu']
        self.sub_menu = self.api['sub-menu']
        self.headers = self.api['headers']
        self.params = self.api['params']
        self.params_sub_menu = self.api['params_product']

        mongo = mongodb_connector.Mongodb()
        self.collection = mongo.connect().get_collection(self.env['mongodb.collection.categories'])
        logging.debug("Mongodb connected")
        self.list_categories = []

    def menu_craw(self):
        response = requests.get(self.menu, headers=self.headers, params=self.params)
        if response is not None:
            data = response.json()
            items = data.get("menu_block", "").get("items", "")
            if items:
                for item in items:
                    link = item.get("link").split("/")
                    url = link[-2]
                    category_id = link[-1].split('c')[-1]
                    logging.debug(category_id)
                    print(category_id)
                    self.sub_menu_craw(url, category_id)
                    self.collection.insert_many(self.list_categories)
                    print("Categories has been inserted")
                    self.list_categories.clear()

            if len(self.list_categories) > 0:
                self.collection.insert_many(self.list_categories)
                self.list_categories.clear()
                print("Categries have been ínserted")

    def sub_menu_craw(self, url, category_id):
        self.params_sub_menu['category'] = category_id
        self.params_sub_menu['urlKey'] = url
        response = requests.get(self.sub_menu, headers=self.headers, params=self.params_sub_menu)
        if response.status_code == 200:
            data = response.json()
            self.list_categories.append(data)
            filters = data.get("filters", "")
            if filters:
                if filters[0].get("query_name", "") == "category":
                    items = filters[0].get("values", "")
                    for item in items:
                        url = item.get("url_key", "")
                        category_id = item.get("query_value", "")
                        print(category_id)
                        logging.debug(category_id)
                        time.sleep(random.randrange(1,4))
                        if len(self.list_categories) == 5:
                            self.collection.insert_many(self.list_categories)
                            print("categories have been insert")
                            self.list_categories.clear()
                        self.sub_menu_craw(url, category_id)


if __name__ == "__main__":
    crawler = CategoriesLinksCrawling()
    crawler.menu_craw()
