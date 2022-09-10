import uuid


class User:
    def __init__(self, username, password):
        self.id = uuid.uuid4()
        self.username = username
        self.password = password

    def validate(self):
        if self.id == '':
            raise ValueError('invalid id')

        if self.username == '':
            raise ValueError('username cannot be empty')

        if self.password == '':
            raise ValueError('password cannot be empty')

        if len(self.password) <= 8:
            raise ValueError('password must be longer than 8 characters')

    def toString(self):
        return str(self.id) + "\n" + self.username + "\n" + self.password
