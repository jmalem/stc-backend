from flask_restful import Resource
from flask import request, abort, jsonify, make_response
from ..repo.view import user as view
from utils import InvalidArgumentError, NotUniqueError
import logging


class Signup(Resource):
    def __init__(self, repo):
        self.repo = repo

    def post(self):
        try:
            data = request.get_json(force=True)
            if data is None:
                raise InvalidArgumentError('Missing body')

            usr = view.from_req_2_model_user(data)
            usr.validate()

            token = self.repo.create(usr)

            return make_response(jsonify({
                'success': True,
                'data': {
                    'username': usr.get_username(),
                    'fullname': usr.get_fullname(),
                    'token': token
                }
            }), 200)
        except NotUniqueError as e:
            logging.error('Failed to signup user ', e)
            abort(400, e)
        except InvalidArgumentError as e:
            logging.error('Failed to signup user ', e)
            abort(400, e)
