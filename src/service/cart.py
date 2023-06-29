import json

from flask_restful import Resource
from flask import abort, jsonify, make_response, request
from utils import InvalidArgumentError, UnauthenticatedError, InternalError, NotFoundError, get_username
import logging
from utils import token_required
from ..repo.view import cart as view


class Cart(Resource):
    def __init__(self, repo, user_repo):
        self.repo = repo
        self.user_repo = user_repo

    @token_required
    def post(self):
        try:
            data = request.get_json(force=True)
            if data is None:
                raise InvalidArgumentError('Missing body')

            cart = view.from_req_2_model_cart(data)
            cart.username = get_username(request.headers)
            cart.validate()

            result = self.repo.create_cart(cart)

            return make_response(jsonify({
                'success': True,
                'data': result
            }), 200)
        except UnauthenticatedError as e:
            logging.error('Failed to create cart ', e)
            abort(401, e)
        except InvalidArgumentError as e:
            logging.error('Failed to create cart ', e)
            abort(400, e)
        except InternalError as e:
            logging.error('Failed to create cart ', e)
            abort(500, e)

    @token_required
    def put(self):
        try:
            data = request.get_json(force=True)
            if data is None:
                raise InvalidArgumentError('Missing body')

            cart = view.from_req_2_model_cart(data)
            cart.username = get_username(request.headers)
            cart.validate()

            result = self.repo.update_cart(cart)

            return make_response(jsonify({
                'success': True,
                'data': result
            }), 200)
        except UnauthenticatedError as e:
            logging.error('Failed to update cart ', e)
            abort(401, e)
        except InvalidArgumentError as e:
            logging.error('Failed to update cart ', e)
            abort(400, e)
        except InternalError as e:
            logging.error('Failed to update cart ', e)
            abort(500, e)

    @token_required
    def get(self):
        try:
            username = get_username(request.headers)
            result = self.repo.get_cart(username)
            return make_response(jsonify({
                'success': True,
                'data': result
            }), 200)
        except UnauthenticatedError as e:
            logging.error('Failed to get cart ', e)
            abort(401, e)
        except InvalidArgumentError as e:
            logging.error('Failed to get cart ', e)
            abort(400, e)
        except NotFoundError as e:
            logging.error('Failed to get cart ', e)
            abort(404, e)
        except InternalError as e:
            logging.error('Failed to get cart ', e)
            abort(500, e)
