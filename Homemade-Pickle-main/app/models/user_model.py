"""
User Model - DynamoDB Version
Table: pickle_users
Partition Key: user_id (String)
"""

import uuid
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from app.db import get_table, USERS_TABLE
from boto3.dynamodb.conditions import Attr


class User(UserMixin):

    def __init__(self, user_data):
        self.id       = user_data.get("user_id")
        self.username = user_data.get("username")
        self.email    = user_data.get("email")
        self.password = user_data.get("password")
        self.role     = user_data.get("role", "user")

    def get_id(self):
        return self.id

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def is_admin(self):
        return self.role == "admin"

    # ── Write ────────────────────────────────────────────────────

    @staticmethod
    def create_user(username, email, password, role="user"):
        table = get_table(USERS_TABLE)
        table.put_item(Item={
            "user_id":    str(uuid.uuid4()),
            "username":   username,
            "email":      email,
            "password":   generate_password_hash(password),
            "role":       role,
            "created_at": datetime.utcnow().isoformat()
        })

    # ── Read ─────────────────────────────────────────────────────

    @staticmethod
    def find_by_id(user_id):
        try:
            table = get_table(USERS_TABLE)
            resp = table.get_item(Key={"user_id": user_id})
            data = resp.get("Item")
            return User(data) if data else None
        except Exception:
            return None

    @staticmethod
    def find_by_username(username):
        try:
            table = get_table(USERS_TABLE)
            resp = table.scan(FilterExpression=Attr("username").eq(username))
            items = resp.get("Items", [])
            return User(items[0]) if items else None
        except Exception:
            return None

    @staticmethod
    def find_by_email(email):
        try:
            table = get_table(USERS_TABLE)
            resp = table.scan(FilterExpression=Attr("email").eq(email))
            items = resp.get("Items", [])
            return User(items[0]) if items else None
        except Exception:
            return None

    @staticmethod
    def find_by_username_or_email(value):
        """Used in login — check both username and email"""
        user = User.find_by_username(value)
        if not user:
            user = User.find_by_email(value)
        return user
