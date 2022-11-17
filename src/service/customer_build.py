from flask_restful import Resource
from flask import abort, jsonify, make_response
import logging
from utils import token_required


class CustomerBuild(Resource):
    def __init__(self, repo, user_repo):
        self.repo = repo
        self.user_repo = user_repo

    @token_required
    def post(self):
        try:
            # downloads from gdrive
            self.repo.init()
            # load new customer
            self.repo.load_customer()
            # returns new lists
            result = self.repo.list()

            return make_response(jsonify({
                'success': True,
                'data': {
                    'customer': result
                }
            }), 200)
        except Exception as e:
            logging.error('Failed to list customer ', e)
            abort(500, e)
