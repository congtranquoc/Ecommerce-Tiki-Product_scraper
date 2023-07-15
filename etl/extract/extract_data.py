from bs4 import BeautifulSoup


class ExtractDescription:

    @staticmethod
    def extract_data(doc):
        id_product = doc.get("id", "")
        product_name = doc.get("name", "")
        short_description = doc.get("short_description", "")
        url = doc.get("short_url", "")
        description = doc.get("description", "")
        rating = doc.get("rating_average", "")
        sold_quantity = doc.get("quantity_sold")
        val = 0
        if sold_quantity:
            val = sold_quantity.get("value") or 0
        price = doc.get("price") or 0
        category = doc.get("categories", {})
        category_id = 0
        if category:
            category_id = category.get("id", "")
        day_ago_created = doc.get("day_ago_created") or 0
        # Làm sạch mô tả bằng cách loại bỏ các tag HTML thừa
        soup = BeautifulSoup(description, "html.parser")
        cleaned_description = soup.get_text().replace("\n", "")

        return (id_product, product_name, short_description, url, cleaned_description, rating, val, price, category_id,
                day_ago_created)
