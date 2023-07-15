from config import mongodb_connector
from envyaml import EnvYAML
from urllib.error import URLError, HTTPError
import requests
import random
import time
import csv
import logging


class ProductIDSpider:

    def __init__(self):
        self.env = EnvYAML('../config/config.yaml')
        self.api = self.env['api']
        self.sub_menu = self.api['sub-menu']
        self.headers = self.api['headers']
        self.params_sub_menu = self.api['params_product']
        self.product_error = self.env['csv.call_api_error']

        mongodb = mongodb_connector.Mongodb()
        self.collection_categories = mongodb.connect().get_collection(self.env['mongodb.collection.categories'])
        self.collection_ids = mongodb.connect().get_collection(self.env['mongodb.collection.ids'])
        self.list_ids = []
        logging.debug("Mongodb connected")

    def checkpoint_categories(self, category, page):
        with open(self.product_error, 'a', newline='') as file:
            writer = csv.writer(file)
            # if csv is empty, the header will be added
            if file.tell() == 0:
                writer.writerow(['category, page'])
            writer.writerow([category, page])

    def get_category(self):
        #Query
        results = self.collection_categories.distinct("query_value")
        for item in results:
            self.product_ids_craw(item, 1)

    def product_ids_craw(self, category_id, page):
        self.params_sub_menu['category'] = category_id
        self.params_sub_menu['page'] = page
        try:
            response = requests.get(self.sub_menu, headers=self.headers, params=self.params_sub_menu)
            if response.status_code == 200:
                data = response.json().get("data", "")
                if data:
                    for item in data:
                        product_id = item.get("id", "")
                        self.list_ids.append({"id": product_id})
                    last_page = response.json().get("paging", {}).get("last_page")
                    current_page = response.json().get("paging", {}).get("current_page")

                    # Insert to mongodb after getting 100 ids
                    if len(self.list_ids) == 100:
                        self.collection_ids.insert_many(self.list_ids)
                        self.list_ids.clear()

                    # The system will sleep random 5-10s
                    if int(current_page) % 5 == 0:
                        print("sleep")
                        time.sleep(random.randrange(3, 5))

                    # Increase pages
                    if last_page > current_page:
                        page += 1
                        self.product_ids_craw(category_id, page)
                if 0 < len(self.list_ids):
                    self.collection_ids.insert_many(self.list_ids)
                    self.list_ids.clear()
        except (URLError, HTTPError, Exception) as e:
            print(f"An error {e} occurs - at {category_id} page {page}")
            self.checkpoint_categories(category_id, page)


if __name__ == "__main__":
    product = ProductIDSpider()
    product.get_category()
