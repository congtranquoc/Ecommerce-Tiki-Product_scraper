from config.MongoDBConnector import MongoManager
from config.MySQLConnector import MysqlManager
from envyaml import EnvYAML
from etl.extract.extract_data import ExtractDescription
import utils


class transfrom_data:

    def __init__(self):
        self.env = utils.getEnv()
        # connection database
        self.mongo_manager = MongoManager.getInstance()
        self.mongo_manager.connect()

        self.mysql_manager = MysqlManager.getInstance()
        self.mysql_manager.connect()

    def transform(self):
        if not self.mysql_manager.check_database_exists():
            self.mysql_manager.create_db()
            self.mysql_manager.create_tiki_table()
        else:
            if not self.mysql_manager.check_table_exists():
                self.mysql_manager.create_tiki_table()

        results = self.mongo_manager.get_information_product()
        list_data = []
        for doc in results:
            data = ExtractDescription.extract_data(doc)
            list_data.append(data)
            if len(list_data) == 200:
                print(f"insert into mysql")
                self.mysql_manager.insert_many_tiki_product(list_data)
                list_data.clear()

        if len(list_data) == 3000:
            self.mysql_manager.insert_many_tiki_product(list_data)
            list_data.clear()

        self.mysql_manager.close_mysql()


if __name__ == "__main__":
    tranfers = transfrom_data()
    tranfers.transform()
