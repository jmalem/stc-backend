from flask_restful import Resource
from flask import request, abort
from ..repo.view import user as view
from pkg import InvalidArgumentError


class Signup(Resource):
    def __init__(self, repo):
        self.repo = repo

    def post(self):
        try:
            data = request.get_json(force=True)
            if data is None:
                raise InvalidArgumentError('Missing body')

            usr = view.from_req_2_model(data)
            usr.validate()

            self.repo.create(usr)

            return 200

        except InvalidArgumentError as e:
            abort(400, e)

