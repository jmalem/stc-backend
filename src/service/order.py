import json

from flask_restful import Resource
from flask import abort, jsonify, make_response, request
from utils import InvalidArgumentError, UnauthenticatedError, InternalError
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
