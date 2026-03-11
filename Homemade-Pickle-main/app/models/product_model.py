"""
Product Model - DynamoDB Version
Table: pickle_products
Partition Key: product_id (String)
"""

import uuid
from datetime import datetime
from app.db import get_table, PRODUCTS_TABLE
from boto3.dynamodb.conditions import Attr
from decimal import Decimal


class Product:

    @staticmethod
    def create_product(name, price, description, stock=0, image_url=None):
        table = get_table(PRODUCTS_TABLE)
        product_id = str(uuid.uuid4())
        table.put_item(Item={
            "product_id":  product_id,
            "name":        name,
            "price":       Decimal(str(price)),
            "description": description,
            "stock":       int(stock),
            "image_url":   image_url or "/static/images/default-product.jpg",
            "created_at":  datetime.utcnow().isoformat()
        })
        return product_id

    @staticmethod
    def get_all_products():
        table = get_table(PRODUCTS_TABLE)
        resp = table.scan()
        items = resp.get("Items", [])
        return Product._convert_list(items)

    @staticmethod
    def find_by_id(product_id):
        try:
            table = get_table(PRODUCTS_TABLE)
            resp = table.get_item(Key={"product_id": product_id})
            item = resp.get("Item")
            return Product._convert(item) if item else None
        except Exception:
            return None

    @staticmethod
    def update_product(product_id, data):
        table = get_table(PRODUCTS_TABLE)
        # Build update expression dynamically
        update_expr = "SET " + ", ".join(f"#{k} = :{k}" for k in data)
        expr_names  = {f"#{k}": k for k in data}
        expr_values = {}
        for k, v in data.items():
            if isinstance(v, float):
                expr_values[f":{k}"] = Decimal(str(v))
            elif isinstance(v, datetime):
                expr_values[f":{k}"] = v.isoformat()
            else:
                expr_values[f":{k}"] = v

        table.update_item(
            Key={"product_id": product_id},
            UpdateExpression=update_expr,
            ExpressionAttributeNames=expr_names,
            ExpressionAttributeValues=expr_values
        )

    @staticmethod
    def delete_product(product_id):
        table = get_table(PRODUCTS_TABLE)
        table.delete_item(Key={"product_id": product_id})

    @staticmethod
    def search_products(query):
        table = get_table(PRODUCTS_TABLE)
        resp = table.scan(
            FilterExpression=(
                Attr("name").contains(query) |
                Attr("description").contains(query)
            )
        )
        return Product._convert_list(resp.get("Items", []))

    @staticmethod
    def deduct_stock(product_id, quantity):
        """Safely deduct stock after order"""
        table = get_table(PRODUCTS_TABLE)
        table.update_item(
            Key={"product_id": product_id},
            UpdateExpression="SET stock = stock - :q",
            ExpressionAttributeValues={":q": int(quantity)}
        )

    # ── Helpers ──────────────────────────────────────────────────

    @staticmethod
    def _convert(item):
        """Convert Decimal to float for templates"""
        if not item:
            return None
        item = dict(item)
        if "price" in item:
            item["price"] = float(item["price"])
        # Use product_id as _id so templates work same way
        item["_id"] = item.get("product_id", "")
        return item

    @staticmethod
    def _convert_list(items):
        return [Product._convert(i) for i in items]
