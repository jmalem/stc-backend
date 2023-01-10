import json

from flask_restful import Resource
from flask import abort, jsonify, make_response, request
from utils import InvalidArgumentError, UnauthenticatedError, InternalError, get_role, get_username
import logging
from utils import token_required
from ..repo.view import order as view


class Order(Resource):
    def __init__(self, repo, user_repo):
        self.repo = repo
        self.user_repo = user_repo

    @token_required
    def post(self):
        try:
            data = request.get_json(force=True)
            if data is None:
                raise InvalidArgumentError('Missing body')

            order = view.from_req_2_model_order(data)
            order.validate()

            result = self.repo.create(order)

            return make_response(jsonify({
                'success': True,
                'data': result
            }), 200)
        except UnauthenticatedError as e:
            logging.error('Failed to create order ', e)
            abort(401, e)
        except InvalidArgumentError as e:
            logging.error('Failed to create order ', e)
            abort(400, e)
        except InternalError as e:
            logging.error('Failed to create order ', e)
            abort(500, e)

    @token_required
    def get(self):
        try:
            flter = request.args
            role = get_role(request.headers)
            if role != 'ADMIN' and role != 'USER':
                return {
                           "message": "Action not allowed!",
                           "data": None,
                           "error": "Unauthorized"
                       }, 401
            username = get_username(request.headers)
            user = self.user_repo.get(username)
            name = user.get('fullname', '')
            result = self.repo.list_orders(flter.to_dict(), role, name)

            return make_response(jsonify({
                'success': True,
                'data': {
                    'orders': result
                }
            }), 200)
        except UnauthenticatedError as e:
            logging.error('Failed to list orders ', e)
            abort(401, e)
        except InvalidArgumentError as e:
            logging.error('Failed to list orders ', e)
            abort(400, e)
        except InternalError as e:
            logging.error('Failed to list orders ', e)
            abort(500, e)
