import datetime

from boto3.dynamodb.conditions import Key, Attr
from botocore.exceptions import ClientError
import logging
from utils import \
    InternalError, NotUniqueError, NotFoundError, InvalidArgumentError

from src.repo.model.cart import Cart as CartModel, CartSchema

logger = logging.getLogger(__name__)
CUSTOMER = 'customer'
CREATEDBY = 'createdBy'
BEFORE = 'toDate'
AFTER = 'fromDate'


class Cart:
    def __init__(self, dyn_resource):
        self.dyn_resource = dyn_resource
        self.table = None

    # check wether the table exist in dynamo db
    def exists(self, table_name):
        try:
            table = self.dyn_resource.Table(table_name)
            table.load()
            exists = True
        except ClientError as err:
            if err.response['Error']['Code'] == 'ResourceNotFoundException':
                exists = False
            else:
                logger.error(
                    "Couldn't check for existence of %s. Here's why: %s: %s",
                    table_name,
                    err.response['Error']['Code'], err.response['Error']['Message'])
                raise
        else:
            self.table = table
        return exists

    def create_table(self, table_name):
        try:
            self.table = self.dyn_resource.create_table(
                TableName=table_name,
                KeySchema=[
                    {'AttributeName': 'username', 'KeyType': 'HASH'},  # Partition key
                    {'AttributeName': 'metadata', 'KeyType': 'RANGE'},  # Sort key
                ],
                AttributeDefinitions=[
                    {'AttributeName': 'username', 'AttributeType': 'S'},
                    {'AttributeName': 'metadata', 'AttributeType': 'S'},
                ],
                ProvisionedThroughput={'ReadCapacityUnits': 3, 'WriteCapacityUnits': 3})
            self.table.wait_until_exists()
        except ClientError as err:
            logger.error(
                "Couldn't create table %s. Here's why: %s: %s", table_name,
                err.response['Error']['Code'], err.response['Error']['Message'])
            raise
        else:
            return self.table

    # List Tables
    def list_tables(self):
        """
        Lists the Amazon DynamoDB tables for the current account.
        :return: The list of tables.
        """
        try:
            tables = []
            for table in self.dyn_resource.tables.all():
                tables.append(table)
        except ClientError as err:
            logger.error(
                "Couldn't list tables. Here's why: %s: %s",
                err.response['Error']['Code'], err.response['Error']['Message'])
            raise
        else:
            return tables

    # will never return undefined
    def get_cart(self, username):
        try:
            response = self.table.get_item(
                Key={
                    'username': username,
                    'metadata': 'cart'
                },
            )
            result = response.get('Item', None)
            if result is None:
                result = self.create_cart(CartModel(username, [], "", 0, 0, ""))
            return result

        except ClientError as err:
            logger.error("couldnt get cart. Here's why: %s", err)
            raise InternalError

    def create_cart(self, cart: CartModel):
        try:
            schema = CartSchema()
            json_result = schema.dump(cart)
            self.table.put_item(
                Item=json_result,
                ConditionExpression="attribute_not_exists(username) AND attribute_not_exists(metadata)",
                ReturnValues='ALL_OLD'
            )
        except ClientError as err:
            if err.response['Error']['Code'] == 'ConditionalCheckFailedException':
                raise NotUniqueError('Not unique')
            logger.error("couldnt create cart. Here's why: %s", err)
            raise InternalError
        else:
            return json_result

    def update_cart(self, cart: CartModel):
        try:
            schema = CartSchema()
            json_result = schema.dump(cart)
            self.table.put_item(
                Item=json_result,
                ConditionExpression="attribute_exists(username) AND attribute_exists(metadata)",
                ReturnValues='NONE'
            )
        except ClientError as err:
            if err.response['Error']['Code'] == 'ConditionalCheckFailedException':
                raise NotFoundError('Not found')
            logger.error("couldnt update cart. Here's why: %s", err)
            raise InternalError
        else:
            return json_result