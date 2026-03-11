# """
# AWS DynamoDB Table Setup Script
# Run this ONCE after you get AWS access to create all 3 tables.

# Usage:
#     python create_tables.py
# """

# import boto3
# import os
# from dotenv import load_dotenv

# load_dotenv()

# dynamodb = boto3.client(
#     'dynamodb',
#     region_name=os.getenv('AWS_REGION', 'ap-south-1'),
#     aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
#     aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY')
# )


# def create_table(table_name, partition_key):
#     try:
#         dynamodb.create_table(
#             TableName=table_name,
#             KeySchema=[
#                 {'AttributeName': partition_key, 'KeyType': 'HASH'}
#             ],
#             AttributeDefinitions=[
#                 {'AttributeName': partition_key, 'AttributeType': 'S'}
#             ],
#             BillingMode='PAY_PER_REQUEST'  # Free tier friendly
#         )
#         print(f"  ✓ Table '{table_name}' created successfully!")
#     except dynamodb.exceptions.ResourceInUseException:
#         print(f"  ℹ Table '{table_name}' already exists — skipping.")
#     except Exception as e:
#         print(f"  ✗ Error creating '{table_name}': {e}")


# if __name__ == '__main__':
#     print("\n" + "="*50)
#     print("  🥒  Creating DynamoDB Tables for Pickle Snacks")
#     print("="*50)

#     create_table('pickle_users',    'user_id')
#     create_table('pickle_products', 'product_id')
#     create_table('pickle_orders',   'order_id')

#     print("\n  ✅ All tables created! Now run: python run.py")
#     print("="*50 + "\n")




"""
AWS DynamoDB Table Setup Script
Run this ONCE after you get AWS access to create all 3 tables.

Usage:
    python create_tables.py
"""

import boto3
import os
from dotenv import load_dotenv

load_dotenv()

dynamodb = boto3.client(
    "dynamodb",
    region_name=os.getenv("AWS_REGION", "ap-south-1"),
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    aws_session_token=os.getenv("AWS_SESSION_TOKEN")  # required for AWS lab credentials
)


def create_table(table_name, partition_key):
    try:
        dynamodb.create_table(
            TableName=table_name,
            KeySchema=[
                {"AttributeName": partition_key, "KeyType": "HASH"}
            ],
            AttributeDefinitions=[
                {"AttributeName": partition_key, "AttributeType": "S"}
            ],
            BillingMode="PAY_PER_REQUEST"  # free-tier friendly
        )

        print(f"✓ Table '{table_name}' created successfully!")

    except dynamodb.exceptions.ResourceInUseException:
        print(f"ℹ Table '{table_name}' already exists — skipping.")

    except Exception as e:
        print(f"✗ Error creating '{table_name}': {e}")


if __name__ == "__main__":

    print("\n" + "=" * 50)
    print("🥒 Creating DynamoDB Tables for Pickle Snacks")
    print("=" * 50)

    create_table("pickle_users", "user_id")
    create_table("pickle_products", "product_id")
    create_table("pickle_orders", "order_id")

    print("\n✅ All tables created! Now run: python run.py")
    print("=" * 50 + "\n")