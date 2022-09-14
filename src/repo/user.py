import hashlib
import bcrypt
from botocore.exceptions import ClientError
import logging
from pkg import InternalError, NotUniqueError
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
                    {'AttributeName': 'username', 'KeyType': 'HASH'},  # Partition key
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

    def create(self, usr: UserModel):
        try:
            salt = bcrypt.gensalt()
            password_hash = User.hash_password(usr.get_password(), salt)
            self.table.put_item(
                Item={
                    'username': usr.get_username(),
                    'hash': password_hash,
                    'salt': salt,
                },
                ConditionExpression="attribute_not_exists(username)",
                ReturnValues='NONE'
            )
        # TODO jansen: add error handling for duplicate, add proper logging, and response
        except ClientError as err:
            logger.error(
                "Couldn't create item. Here's why: %s: %s",
                err.response['Error']['Code'], err.response['Error']['Message'])
            if err.response['Error']['Code'] == 'ConditionalCheckFailedException':
                raise NotUniqueError('Not unique')
            raise InternalError
        else:
            return

    @staticmethod
    def hash_password(password: str, salt: str) -> str:
        combined = str(password) + str(salt)
        return hashlib.sha512(combined.encode("utf-8")).hexdigest()
