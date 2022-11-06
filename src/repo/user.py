import hashlib
import bcrypt
from botocore.exceptions import ClientError
import logging
from utils import \
    InternalError, NotUniqueError, UnauthenticatedError, NotFoundError, \
    hash_password, verify_password, \
    create_jwt, generate_payload
from src.repo.model.user import User as UserModel

logger = logging.getLogger(__name__)


class User:
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
                    {
                        'AttributeName': 'username',
                        'KeyType': 'HASH'
                    },  # Partition key
                ],
                AttributeDefinitions=[
                    {'AttributeName': 'username', 'AttributeType': 'S'},
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

    def create(self, user: UserModel):
        try:
            salt = bcrypt.gensalt()
            password_hash = hash_password(user.get_password(), salt)
            self.table.put_item(
                Item={
                    'username': user.get_username(),
                    'fullname': user.get_fullname(),
                    'role': user.get_role(),
                    'hash': password_hash,
                    'salt': salt,
                },
                ConditionExpression="attribute_not_exists(username)",
                ReturnValues='NONE'
            )
            payload = generate_payload(user.get_username())
            return create_jwt(payload)
        except ClientError as err:
            if err.response['Error']['Code'] == 'ConditionalCheckFailedException':
                raise NotUniqueError('Not unique')
            raise InternalError
        else:
            return

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

    def login(self, user: UserModel):
        try:
            response = self.table.get_item(
                Key={
                    'username': user.get_username()
                }
            )
            data = response.get('Item')
            if data is None:
                raise UnauthenticatedError('invalid username/password')

            if verify_password(user.get_password(), str(bytes(data['salt'])), data['hash']):
                payload = generate_payload(user.get_username())
                return {
                    'token': create_jwt(payload),
                    'fullname': data['fullname'],
                    'role': data['role']
                }

            raise UnauthenticatedError('invalid username/password')
        except ClientError as e:
            raise InternalError
