from envyaml import EnvYAML
from pymongo import MongoClient
from urllib.parse import quote_plus

# read file env.yaml and parse config
env = EnvYAML('../config/config.yaml')


class Mongodb:
    def connect(self):
        mongodb_config = env['mongodb']
        host = mongodb_config['host']
        username = quote_plus(mongodb_config['username'])
        pwd = quote_plus(mongodb_config['password'])
        database = mongodb_config['database']

        # create string to connetion mongodb
        # connection_string = f"mongodb://{username}:{pwd}@{host}/{database}"
        connection_string = f"mongodb://{host}:27017"

        # connection
        client = MongoClient(connection_string)
        db = client[database]
        return db