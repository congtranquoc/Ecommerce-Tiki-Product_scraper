from config import mongodb_connector
from envyaml import EnvYAML
from concurrent.futures import ThreadPoolExecutor
from itertools import islice
from urllib.error import URLError, HTTPError
from urllib.request import urlopen
import requests
import random
import time
import traceback
import csv
import os
import shutil
import logging

class ProductIDSpider:

    def __init__(self):
        self.env = EnvYAML('../config/config.yaml')
        self.api = self.env['api']
        self.sub_menu = self.api['sub-menu']
        self.headers = self.api['headers']
        self.params_sub_menu = self.api['params_product']
        self.product_error= self.env['csv.call_api_error']

        mongo = mongodb_connector.Mongodb()
        self.collection = mongo.connect().get_collection(self.env['mongodb.collection.categories'])
        logging.debug("Mongodb connected")

    def checkpoint_product(self,category, page):
        with open(self.product_error, 'a', newline='') as file:
            writer = csv.writer(file)

            #if csv is empty, the header will be added
            if file.tell() == 0:
                writer.writerow(['category, page'])
            writer.writerow([category,page])

    def get_category(self):
        # Thực hiện câu lệnh truy vấn
        result = self.collection.find(
            {
                'filters': {
                    '$elemMatch': {
                        'values': {'query_value': 0},
                        'values.query_name': 'category'
                    }
                }
            },
            {
                 '_id': 0,
                 'filters.values.query_value': 1
            }
        )

        for item in result[:2]:
            print(item)

if __name__ == "__main__":
    product = ProductIDSpider()
    product.get_category()