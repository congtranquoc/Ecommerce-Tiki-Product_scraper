import multiprocessing
from concurrent.futures import ThreadPoolExecutor

from config import mongodb_connector
from envyaml import EnvYAML
from urllib.error import URLError, HTTPError
import requests
import random
import time
import csv
import json
import logging

class ProductDataSpider:

    def __init__(self):
        self.env = EnvYAML('../config/config.yaml')
        self.api = self.env['api']
        self.product_api = self.api['product']
        self.headers = self.api['headers']
        self.params = self.api['params']
        self.product_error = self.env['csv.call_product_error']
        mongodb = mongodb_connector.Mongodb()
        self.collection_products = mongodb.connect().get_collection(self.env['mongodb.collection.products'])
        self.collection_ids = mongodb.connect().get_collection(self.env['mongodb.collection.ids'])
        self.list_detail_product = []
        logging.debug("Mongodb connected")

    #Check point, save all product ids if the request get an error
    def checkpoint_products(self, pid):
        with open(self.product_error, 'a', newline='') as file:
            writer = csv.writer(file)
            # if csv is empty, the header will be added
            if file.tell() == 0:
                writer.writerow(['id'])
            writer.writerow([pid])

    #Get all product ids from mongodb
    def get_product_ids(self):
        # Query
        # results = self.collection_ids.distinct("id") ->  error distinct too big, 16mb cap
        results = [x['id'] for x in self.collection_ids.find({}, {'id': 1})]

        # Create a process pool with a maximum of 3 workers
        with ThreadPoolExecutor(max_workers=3) as exc:
            for item in results:
                # Map the detail_products_craw function to each product ID
                future = exc.submit(self.detail_products_craw, item)
                print(future.done())

        if len(self.list_detail_product) > 0:
            # insert data into MongoDB
            self.collection_products.insert_many(self.list_detail_product)

    #Get detail product from api tiki
    def detail_products_craw(self, pid):
        try:
            response = requests.get(self.product_api(pid), headers=self.headers, params=self.params)
            if response.status_code == 200:
                try:
                    data = response.json()
                    self.list_detail_product.append(data)
                    print(pid)
                    if len(self.list_detail_product) == 100:
                        # insert data into MongoDB
                        self.collection_products.insert_many(self.list_detail_product)
                        time.sleep(5)
                except json.JSONDecodeError as e:
                    print(f"Error decoding JSON for product {pid}: {e}")
                    self.checkpoint_products(pid)
                    time.sleep(3)
                time.sleep(random.randrange(3))
            else:
                print(f"get {pid} error with status {response.status_code}")
                self.checkpoint_products(pid)
                time.sleep(3)
        except (URLError, HTTPError, Exception) as e:
            print(f"Error opening {pid}")
            self.checkpoint_products(pid)
            time.sleep(3)

if __name__ == "__main__":
    detail = ProductDataSpider()
    detail.get_product_ids()