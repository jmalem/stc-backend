from flask_restful import Resource
from flask import request, abort, jsonify, make_response
from ..repo.view import user as view
from utils import InvalidArgumentError, UnauthenticatedError, InternalError
import logging


class Login(Resource):
    def __init__(self, repo):
        self.repo = repo

    def post(self):
        try:
            data = request.get_json(force=True)
            if data is None:
                raise InvalidArgumentError('Missing body')

            usr = view.from_req_2_model(data)
            usr.validate()

            token = self.repo.login(usr)

            return make_response(jsonify({
                'success': True,
                'data': {
                    'token': token
                }
            }), 200)
        except UnauthenticatedError as e:
            logging.error('Failed to login ', e)
            abort(401, e)
        except InvalidArgumentError as e:
            logging.error('Failed to login ', e)
            abort(400, e)
        except InternalError as e:
            logging.error('Failed to login ', e)
            abort(500, e)