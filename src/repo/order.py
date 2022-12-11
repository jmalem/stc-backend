import datetime

from boto3.dynamodb.conditions import Key, Attr
from botocore.exceptions import ClientError
import logging
from utils import \
    InternalError, NotUniqueError, NotFoundError, InvalidArgumentError

from src.repo.model.order import Order as OrderModel, OrderSchema

logger = logging.getLogger(__name__)
CUSTOMER = 'customer'
BEFORE = 'before'
AFTER = 'after'


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
                    {'AttributeName': 'customer', 'KeyType': 'HASH'},  # Partition key
                    {'AttributeName': 'id', 'KeyType': 'RANGE'},  # Sort key
                ],
                AttributeDefinitions=[
                    {'AttributeName': 'customer', 'AttributeType': 'S'},
                    {'AttributeName': 'id', 'AttributeType': 'S'},
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
            order.createdAt = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")

            schema = OrderSchema()
            json_result = schema.dump(order)
            self.table.put_item(
                Item=json_result,
                ConditionExpression="attribute_not_exists(customer) AND attribute_not_exists(id)",
                ReturnValues='ALL_OLD'
            )
        except ClientError as err:
            if err.response['Error']['Code'] == 'ConditionalCheckFailedException':
                raise NotUniqueError('Not unique')
            raise InternalError
        else:
            return json_result

    def get(self, customer):
        try:
            response = self.table.get_item(
                Key={
                    'customer': customer,
                },
            )
        except ClientError as err:
            if err.response['Error']['Code'] == 'ResourceNotFoundException':
                raise NotFoundError('Not found')
            raise InternalError
        else:
            return response['Item']

    def list_orders(self, filters):
        try:
            if type(filters) is not dict:
                raise InternalError('Filter type error')
            customer = filters.get(CUSTOMER, '')
            before = filters.get(BEFORE, None)
            after = filters.get(AFTER, None)
            cond = None

            if after is not None:
                cond = Attr('createdAt').gte(after)

            if before is not None:
                if cond is None:
                    cond = Attr('createdAt').lte(before)
                else:
                    cond = cond & Attr('createdAt').lte(before)

            cond_kwargs = {}
            if cond:
                cond_kwargs['FilterExpression'] = cond
            # optimise using query when we have customer
            if customer != "":
                response = self.table.query(
                    KeyConditionExpression=Key('customer').eq(customer),
                    **cond_kwargs
                )
            # we have to scan when customer is not specified
            else:
                response = self.table.scan(
                    **cond_kwargs
                )

        except ClientError as err:
            if err.response['Error']['Code'] == 'ResourceNotFoundException':
                raise NotFoundError('Not found')
            raise InternalError
        else:
            return response['Items']
