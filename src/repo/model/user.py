import uuid
from utils import InvalidArgumentError
from marshmallow import Schema, fields

allowed_role = ['ADMIN', 'USER', 'GUEST', 'ADMIN_VIEW_OLD_EMPTY']


class User:
    def __init__(self, username, password, fullname, role):
        self.username = username
        self.password = password
        self.fullname = fullname
        self.role = role

    def validate_login(self):
        if self.username == '':
            raise InvalidArgumentError('username cannot be empty')

        if self.password == '':
            raise InvalidArgumentError('password cannot be empty')

        if len(self.password) < 8:
            raise InvalidArgumentError(
                'password must be at least 8 characters')

    def validate(self):
        self.validate_login()

        if self.fullname == '':
            raise InvalidArgumentError('fullname cannot be empty')

        if self.role == '':
            raise InvalidArgumentError('role cannot be empty')

        if self.role not in allowed_role:
            raise InvalidArgumentError('role is invalid')

    def get_username(self) -> str:
        return self.username

    def get_password(self) -> str:
        return self.password

    def get_fullname(self) -> str:
        return self.fullname

    def get_role(self) -> str:
        return self.role

    def toString(self) -> str:
        return self.username + "\n" + self.password
