import uuid
from utils import InvalidArgumentError
from marshmallow import Schema, fields


class User:
    def __init__(self, username, password):
        self.username = username
        self.password = password

    def validate(self):
        if self.username == '':
            raise InvalidArgumentError('username cannot be empty')

        if self.password == '':
            raise InvalidArgumentError('password cannot be empty')

        if len(self.password) <= 8:
            raise InvalidArgumentError('password must be longer than 8 characters')

    def get_username(self) -> str:
        return self.username

    def get_password(self) -> str:
        return self.password

    def toString(self) -> str:
        return self.username + "\n" + self.password

