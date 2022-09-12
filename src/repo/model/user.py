import uuid
from pkg import InvalidArgumentError


class User:
    def __init__(self, username, password):
        self.id = uuid.uuid4()
        self.username = username
        self.password = password

    def validate(self):
        if self.id == '':
            raise InvalidArgumentError('invalid id')

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
        return str(self.id) + "\n" + self.username + "\n" + self.password
