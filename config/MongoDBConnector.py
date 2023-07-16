from urllib.parse import quote_plus

from pymongo import MongoClient

import utils


class MongoManager:
    __instance = None

    @staticmethod
    def getInstance():
        if MongoManager.__instance is None:
            MongoManager.__instance = MongoManager()
        return MongoManager.__instance

    def __init__(self):
        if MongoManager.__instance is not None:
            raise Exception("This class is a singleton!")
        # read file env.yaml and parse config
        self.env = utils.getEnv()
        self.mongodb_config = self.env['mongodb']
        self.host = self.mongodb_config['host']
        self.username = quote_plus(self.mongodb_config['username'])
        self.pwd = quote_plus(self.mongodb_config['password'])
        self.database = self.mongodb_config['database']
        self.categories = self.env['mongodb.collection.categories']
        self.ids = self.env['mongodb.collection.ids']
        self.products = self.env['mongodb.collection.products']
        self.mongo = None
        self.client = None
        MongoManager.__instance = self

    def connect(self):
        # create string to connection mongodb
        # connection_string = f"mongodb://{username}:{pwd}@{host}/{database}"
        connection_string = f"mongodb://{self.host}:27017"
        # connection
        self.client = MongoClient(connection_string)
        self.mongo = self.client[self.database]

    def get_collection_categories(self):
        return self.mongo.get_collection(self.categories)

    def get_collection_ids(self):
        return self.mongo.get_collection(self.ids)

    def get_collection_products(self):
        return self.mongo.get_collection(self.products)

    def get_information_product(self):
        # Thực hiện truy vấn aggregate
        pipeline = [
            {
                "$project": {
                    "_id": 0,
                    "id": 1,
                    "name": 1,
                    "short_description": 1,
                    "short_url": 1,
                    "description": 1,
                    "rating_average": 1,
                    "quantity_sold.value": 1,
                    "quantity_sold.price": 1,
                    "categories.id": 1,
                    "day_ago_created": 1
                }
            }
        ]

        results = self.get_collection_products().aggregate(pipeline)
        return list(results)

    def count_categories(self):
        # Thực hiện truy vấn để thống kê số lượng sản phẩm cho mỗi danh mục
        pipeline = [
            {
                '$group': {
                    '_id': '$categories.name',
                    'count': {'$sum': 1}
                }
            }
        ]

        results = self.get_collection_products().aggregate(pipeline)
        return list(results)

    def count_origin_data(self):
        pipeline = [
            {
                '$unwind': '$specifications'
            },
            {
                '$unwind': '$specifications.attributes'
            },
            {
                '$match': {
                    'specifications.attributes.code': 'origin'
                }
            },
            {
                '$group': {
                    '_id': '$specifications.attributes.value',
                    'count': {'$sum': 1}
                }
            },
            {
                '$match': {
                    '_id': {'$ne': None}
                }
            }
        ]

        result = self.get_collection_products().aggregate(pipeline)
        return list(result)

    def close_connection(self):
        if self.client is not None:
            self.client.close()
