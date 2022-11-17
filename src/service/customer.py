from flask_restful import Resource
from flask import abort, jsonify, make_response
from utils import UnauthenticatedError, InternalError
import logging
from utils import token_required


class Customer(Resource):
    def __init__(self, repo, user_repo):
        self.repo = repo
        self.user_repo = user_repo

    @token_required
    def get(self):
        try:
            res = self.repo.list()
            print(res)
            return make_response(jsonify({
                'success': True,
                'data': {
                    'customers': res
                }
            }), 200)
        except UnauthenticatedError as e:
            logging.error('Failed to list customers ', e)
            abort(401, e)
        except InternalError as e:
            logging.error('Failed to list customers ', e)
            abort(500, e)
