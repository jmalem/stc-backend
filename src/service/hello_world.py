from flask_restful import Resource
from ..repo.model import user


class HelloWorld(Resource):
    def __init__(self, repo):
        self.repo = repo

    def get(self):
        tmp = user.User("User", "something")
        return {'hello': tmp.toString(), 'exists': self.repo.exists('stc-user')}
