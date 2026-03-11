# """
# DynamoDB Connection
# Single place to get DynamoDB table references
# """

# import boto3
# import os


# def get_dynamodb():
#     """Return DynamoDB resource connected to AWS"""
#     return boto3.resource(
#         'dynamodb',
#         region_name=os.getenv('AWS_REGION', 'ap-south-1'),
#         aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
#         aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY')
#     )


# def get_table(table_name):
#     """Return a specific DynamoDB table"""
#     db = get_dynamodb()
#     return db.Table(table_name)


# # Table name constants
# USERS_TABLE    = 'pickle_users'
# PRODUCTS_TABLE = 'pickle_products'
# ORDERS_TABLE   = 'pickle_orders'




"""
DynamoDB Connection
Single place to get DynamoDB table references
"""

import boto3
import os


def get_dynamodb():
    """Return DynamoDB resource connected to AWS"""

    return boto3.resource(
        "dynamodb",
        region_name=os.getenv("AWS_REGION", "ap-south-1"),
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
        aws_session_token=os.getenv("AWS_SESSION_TOKEN")  # needed for AWS labs
    )


def get_table(table_name):
    """Return a specific DynamoDB table"""

    dynamodb = get_dynamodb()
    return dynamodb.Table(table_name)


# ─────────────────────────────
# Table Name Constants
# ─────────────────────────────

USERS_TABLE = "pickle_users"
PRODUCTS_TABLE = "pickle_products"
ORDERS_TABLE = "pickle_orders"