import csv
import os

import matplotlib.pyplot as plt
import pandas as pd

import utils
from config.MongoDBConnector import MongoManager
from config.MySQLConnector import MysqlManager


class StaticData:

    def __init__(self):
        self.env = utils.getEnv()
        # connection database
        self.mongo_manager = MongoManager.getInstance()
        self.mongo_manager.connect()

        self.mysql_manager = MysqlManager.getInstance()
        self.mysql_manager.connect()

    def store_categories_data(self, categories, product_counts):
        # Mở file CSV và ghi dữ liệu
        with open(self.env["csv.static_categories"], mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(['category', 'product'])  # Ghi tiêu đề cột
            for category, count in zip(categories, product_counts):
                writer.writerow([category, count])  # Ghi dữ liệu từng dòng

    def store_countries_data(self, origins, counts):
        # Mở file CSV và ghi dữ liệu
        with open(self.env["csv.origin"], 'w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(['origins', 'counts'])  # Ghi tiêu đề cột
            for origin, count in zip(origins, counts):
                writer.writerow([origin, count])  # Ghi dữ liệu từng dòng

    def store_product_ingredients(self, product_names, ingredients):
        with open(self.env["csv.product_ingredient"], mode="w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(["product_name", "ingredient"])
            for product_name, ingredient in zip(product_names, ingredients):
                writer.writerow([product_name, ingredient])

    def draw_categories_bar_chart(self, df):
        df_sorted = df.sort_values(by='product', ascending=False)
        df_sorted = df_sorted.reset_index(drop=True)
        print(f"Thống kê danh sách danh mục theo sản phẩm \n{df_sorted}\n\n")
        df_subset = df_sorted[:10]

        # Tạo biểu đồ cột ngang
        fig, ax = plt.subplots()
        fig.set_size_inches(10, 8)  # Đặt kích thước theo ý muốn

        # Đặt các đỉnh của cột ngang
        ax.barh(range(len(df_subset)), df_subset['product'], color='steelblue')
        ax.set_yticks(range(len(df_subset)))
        ax.set_yticklabels(df_subset['category'])

        # Đặt tiêu đề và nhãn cho trục x
        ax.set_xlabel('Số lượng sản phẩm')
        ax.set_ylabel('Danh mục')
        ax.set_title('Top 10 danh mục có số lượng sản phẩm nhiều nhất')

        # Tạo chú thích
        for i, category in enumerate(df_subset['category']):
            ax.text(df_subset['product'][i], i, str(df_subset['product'][i]), va='center')

        # Hiển thị biểu đồ
        plt.tight_layout()
        plt.show()

    def visual_category(self):
        # Kiểm tra xem file tồn tại hay không
        if not os.path.exists(self.env["csv.static_categories"]):
            result = self.mongo_manager.count_categories()
            # Dữ liệu danh mục và số lượng sản phẩm
            categories = []
            product_counts = []
            # In kết quả
            for category in result:
                category_name = category['_id']
                product_count = category['count']
                if category_name is not None and product_count is not None:  # Kiểm tra giá trị trước khi thêm vào danh sách
                    categories.append(category_name)
                    product_counts.append(product_count)

            self.store_categories_data(categories, product_counts)
        df = pd.read_csv(self.env["csv.static_categories"])
        self.draw_categories_bar_chart(df)

    def visual_origin(self):
        # Kiểm tra xem file tồn tại hay không
        if not os.path.exists(self.env["csv.origin"]):
            result = self.mongo_manager.count_origin_data()
            # Tạo danh sách xuất xứ và số lượng tương ứng
            origins = []
            counts = []
            for item in result:
                origin = item['_id']
                count = item['count']
                if origin is not None and count is not None:  # Kiểm tra giá trị trước khi thêm vào danh sách
                    origins.append(origin)
                    counts.append(count)
                self.store_countries_data(origins, counts)

        df = pd.read_csv(self.env["csv.origin"])
        print(df.sort_values(by='counts', ascending=False).reset_index(drop=True))

    def visual_product_ingredient(self):
        # Kiểm tra xem file tồn tại hay không
        if not os.path.exists(self.env["csv.product_ingredient"]):
            result = self.mysql_manager.get_products_has_ingredient()
            # Tạo danh sách dữ liệu
            products = []
            ingredients = []
            for product_name, description in result:
                # Trích xuất thông tin thành phần từ miêu tả
                ingredient = ""
                if description:
                    description = description.replace("\n", "")
                    start_index = description.lower().find("thành phần")
                    if start_index != -1:
                        start_index += len("thành phần")
                        end_index = description.find("\n", start_index)
                        ingredient = description[start_index:end_index].strip()
                products.append(product_name)
                ingredients.append(ingredient)

            # Lưu dữ liệu vào file CSV
            self.store_product_ingredients(products, ingredients)

        df = pd.read_csv(self.env["csv.product_ingredient"])
        print(df)


if __name__ == "__main__":
    static_data = StaticData()
    static_data.visual_category()
    static_data.visual_origin()
    static_data.visual_product_ingredient()
