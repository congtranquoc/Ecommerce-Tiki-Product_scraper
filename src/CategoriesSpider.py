import csv
import logging
import time
from urllib.error import URLError, HTTPError

import requests

import utils
from config.MongoDBConnector import MongoManager


class CategoriesLinksCrawling:

    def __init__(self):
        self.env = utils.getEnv()
        self.api = self.env['api']
        self.menu = self.api['menu']
        self.sub_menu = self.api['sub-menu']
        self.headers = self.api['headers']
        self.params = self.api['params']
        self.params_sub_menu = self.api['params_product']

        mongo_manager = MongoManager.getInstance()
        mongo_manager.connect()
        self.collection = mongo_manager.get_collection_categories()
        logging.debug("Mongodb connected")
        self.list_categories = []

    # Write categories which can not be reques - a exception is occurs
    def checkpoint_categories(self, url, category):
        with open('../data/category_ids_error.csv', 'a', newline='') as file:
            writer = csv.writer(file)
            # if csv is empty, the header will be added
            if file.tell() == 0:
                writer.writerow(['urlKey, category'])
            writer.writerow([url, category])

    # request the parent categories
    def menu_craw(self):
        response = requests.get(self.menu, headers=self.headers, params=self.params)
        if response is not None:
            data = response.json()
            items = data.get("menu_block", "").get("items", "")
            if items:
                for item in items:
                    try:
                        link = item.get("link").split("/")
                        url = link[-2]
                        category_id = link[-1].split('c')[-1]
                        logging.debug(category_id)
                        print(category_id)
                        self.sub_menu_craw(url, category_id)
                        self.list_categories.clear()
                    except (URLError, HTTPError, Exception) as e:
                        print(f"An error {e}")
                        self.checkpoint_categories(url, category_id)
            if len(self.list_categories) > 0:
                self.collection.insert_many(self.list_categories)
                self.list_categories.clear()
                print("Categries have been ínserted")

    # request the child categories
    def sub_menu_craw(self, url, category_id):
        try:
            self.params_sub_menu['category'] = category_id
            self.params_sub_menu['urlKey'] = url
            response = requests.get(self.sub_menu, headers=self.headers, params=self.params_sub_menu)
            if response.status_code == 200:
                data = response.json()

                filters = data.get("filters", "")
                if filters:
                    if filters[0].get("query_name", "") == "category":
                        items = filters[0].get("values", "")
                        for item in items:
                            self.list_categories.append(item)
                            url = item.get("url_key", "")
                            category_id = item.get("query_value", "")
                            print(category_id)
                            logging.debug(category_id)
                            time.sleep(1)
                            if len(self.list_categories) == 20:
                                self.collection.insert_many(self.list_categories)
                                print("categories have been insert")
                                self.list_categories.clear()
                            self.sub_menu_craw(url, category_id)
        except (URLError, HTTPError, Exception) as e:
            print(f"An error {e}")
            self.checkpoint_categories(url, category_id)


if __name__ == "__main__":
    crawler = CategoriesLinksCrawling()
    crawler.menu_craw()
