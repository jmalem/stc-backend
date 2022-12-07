from flask_restful import Resource
from flask import abort, jsonify, make_response, request
import logging
from utils import token_required, get_role


class Product(Resource):
    def __init__(self, repo, user_repo):
        self.repo = repo
        self.user_repo = user_repo

    @token_required
    def get(self):
        try:
            role = get_role(request.headers)
            flter = request.args
            result = self.repo.list(flter.to_dict(), role)

            return make_response(jsonify({
                'success': True,
                'data': {
                    'products': result
                }
            }), 200)
        except Exception as e:
            logging.error('Failed to list product ', e)
            abort(500, e)
