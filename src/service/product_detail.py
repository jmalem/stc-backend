from flask_restful import Resource
from flask import abort, jsonify, make_response
import logging
from utils import token_required, NotFoundError


class ProductDetail(Resource):
    def __init__(self, repo, user_repo):
        self.repo = repo
        self.user_repo = user_repo

    @token_required
    def get(self, item_id):
        try:
            result = self.repo.get(item_id)

            return make_response(jsonify({
                'success': True,
                'data': result[0]
            }), 200)
        except NotFoundError as e:
            logging.error('Failed to get product ', e)
            abort(404, e)
        except Exception as e:
            logging.error('Failed to get product ', e)
            abort(500, e)
