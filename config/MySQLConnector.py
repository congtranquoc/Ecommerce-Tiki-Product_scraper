import logging
import mysql.connector
import utils

class MysqlManager:

    __instance = None

    @staticmethod
    def getInstance():
        if MysqlManager.__instance is None:
            MysqlManager.__instance = MysqlManager()
        return MysqlManager.__instance

    def __init__(self):
        if MysqlManager.__instance is not None:
            raise Exception("This class is a singleton!")
        # read file env.yaml and parse config
        self.env = utils.getEnv()
        self.query = self.env['mysql.query']
        # Lấy thông tin kết nối từ biến môi trường
        self.user = self.env['mysql.username']
        self.password = self.env['mysql.password']
        self.host = self.env['mysql.host']
        self.database = self.env['mysql.database']
        self.table = self.env['mysql.table.products']
        self.mysql_cnx = None
        self.mysql_cursor = None
        MysqlManager.__instance = self

    def is_connected(self):
        # Kiểm tra xem đã kết nối tới MySQL hay chưa
        if self.mysql_cnx:
            return self.mysql_cnx.is_connected()
        return False

    def connect(self):
        # Kiểm tra kết nối tới MySQL
        try:
            self.mysql_cnx = mysql.connector.connect(
                user=self.user,
                password=self.password,
                host=self.host,
                # database=self.database  # Thêm thông tin cơ sở dữ liệu vào kết nối
            )
            self.mysql_cursor = self.mysql_cnx.cursor()
        except mysql.connector.Error as err:
            print(f"Lỗi khi kết nối tới MySQL: {err}")
            # Thực hiện xử lý lỗi tại đây (ví dụ: ghi log, thông báo lỗi, vv.)
            logging.error(err)
            raise

    def check_database_exists(self):
        if self.is_connected():
            self.use_data()
            # Kiểm tra xem cơ sở dữ liệu có tồn tại trong MySQL hay không
            self.mysql_cursor.execute(self.query["SHOW_DATABASE"])
            databases = self.mysql_cursor.fetchall()
            databases = [db[0] for db in databases]
            return self.database in databases

    def use_data(self):
        # Sử dụng cơ sở dữ liệu
        use_query = self.query['USE_DATABASE'].format(database=self.database)
        self.mysql_cursor.execute(use_query)

    def check_table_exists(self):
        if self.is_connected():
            self.use_data()
            # Kiểm tra table đã tồn tại chưa
            check_query = self.query["SHOW_TABLE"]
            self.mysql_cursor.execute(check_query)
            tables = self.mysql_cursor.fetchall()
            tables = [table[0] for table in tables]
            return self.table in tables

    def create_db(self):
        if self.is_connected():
            sql_create = self.query['CREATE_DATABASE'].format(database=self.database)
            self.mysql_cursor.execute(sql_create)

    def create_tiki_table(self):
        if self.is_connected():
            # Sử dụng cơ sở dữ liệu
            use_query = self.query['USE_DATABASE'].format(database=self.database)
            self.mysql_cursor.execute(use_query)

            sql_create = self.query["CREATE_TABLE"]
            self.mysql_cursor.execute(sql_create)

    def insert_many_tiki_product(self, datas):
        if self.is_connected():
            sql_insert = self.query["INSERT_PRODUCT"]
            self.mysql_cursor.executemany(sql_insert, datas)
            self.mysql_cnx.commit()

    def get_products_has_ingredient(self):
        if self.is_connected():
            sql = self.query["QUERY_INGREDIENT"].format(table=self.table)
            # Use all the SQL you like
            self.mysql_cursor.execute(sql)
            result = self.mysql_cursor.fetchall()
            return result

    def close_mysql(self):
        if self.is_connected():
            # Đóng con trỏ và kết nối MySQL
            self.mysql_cursor.close()
            self.mysql_cnx.close()
