import json

from botocore.exceptions import ClientError
import logging
from utils import \
    InternalError, NotUniqueError, NotFoundError

from src.repo.model.order import Order as OrderModel, OrderSchema

logger = logging.getLogger(__name__)


class Order:
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
                    {'AttributeName': 'id', 'KeyType': 'HASH'},  # Partition key
                    {'AttributeName': 'customer', 'KeyType': 'RANGE'},  # Sort key
                ],
                AttributeDefinitions=[
                    {'AttributeName': 'id', 'AttributeType': 'S'},
                    {'AttributeName': 'customer', 'AttributeType': 'S'},
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

    def create(self, order: OrderModel):
        try:
            schema = OrderSchema()
            json_result = schema.dump(order)
            self.table.put_item(
                Item=json_result,
                ConditionExpression="attribute_not_exists(username)",
                ReturnValues='ALL_OLD'
            )
        except ClientError as err:
            if err.response['Error']['Code'] == 'ConditionalCheckFailedException':
                raise NotUniqueError('Not unique')
            raise InternalError
        else:
            return json_result

    def get(self, username):
        try:
            response = self.table.get_item(
                Key={
                    'username': username,
                },
            )
        except ClientError as err:
            if err.response['Error']['Code'] == 'ResourceNotFoundException':
                raise NotFoundError('Not found')
            raise InternalError
        else:
            return response['Item']
