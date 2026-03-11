"""
Order Model - DynamoDB Version
Table: pickle_orders
Partition Key: order_id (String)
"""

import uuid
from datetime import datetime
from app.db import get_table, ORDERS_TABLE
from boto3.dynamodb.conditions import Attr
from decimal import Decimal


class Order:

    @staticmethod
    def create_order(user_id, order_items, total_amount):
        table = get_table(ORDERS_TABLE)
        order_id = str(uuid.uuid4())

        # Convert floats to Decimal for DynamoDB
        converted_items = []
        for item in order_items:
            converted_items.append({
                "product_id": item["product_id"],
                "name":       item["name"],
                "price":      Decimal(str(item["price"])),
                "quantity":   int(item["quantity"]),
                "subtotal":   Decimal(str(item["subtotal"]))
            })

        table.put_item(Item={
            "order_id":     order_id,
            "user_id":      user_id,
            "order_items":  converted_items,
            "total_amount": Decimal(str(total_amount)),
            "status":       "completed",
            "created_at":   datetime.utcnow().isoformat()
        })
        return order_id

    @staticmethod
    def find_by_id(order_id):
        try:
            table = get_table(ORDERS_TABLE)
            resp = table.get_item(Key={"order_id": order_id})
            item = resp.get("Item")
            return Order._convert(item) if item else None
        except Exception:
            return None

    @staticmethod
    def find_by_user(user_id):
        try:
            table = get_table(ORDERS_TABLE)
            resp = table.scan(FilterExpression=Attr("user_id").eq(user_id))
            items = resp.get("Items", [])
            converted = [Order._convert(i) for i in items]
            # Sort by created_at descending
            converted.sort(key=lambda x: x.get("created_at", ""), reverse=True)
            return converted
        except Exception:
            return []

    # ── Helpers ──────────────────────────────────────────────────

    @staticmethod
    def _convert(item):
        """Convert Decimal to float and add _id alias"""
        if not item:
            return None
        item = dict(item)
        if "total_amount" in item:
            item["total_amount"] = float(item["total_amount"])
        # Convert order_items decimals
        converted_items = []
        for oi in item.get("order_items", []):
            oi = dict(oi)
            oi["price"]    = float(oi.get("price", 0))
            oi["subtotal"] = float(oi.get("subtotal", 0))
            oi["quantity"] = int(oi.get("quantity", 0))
            converted_items.append(oi)
        item["order_items"] = converted_items
        # Alias for templates
        item["_id"] = item.get("order_id", "")
        return item
