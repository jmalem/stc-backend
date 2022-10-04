from flask_restful import Resource
from flask import abort, jsonify, make_response
import logging
import pandas as pd


class ProductBuild(Resource):
    def __init__(self, repo):
        self.repo = repo

    def post(self):
        try:
            # downloads from gdrive
            self.repo.init()
            # convert to csv
            self.repo.export_to_csv()
            # returns new lists
            result = self.repo.list()
            return make_response(jsonify({
                'success': True,
                'data': {
                    'products': result
                }
            }), 200)
        except Exception as e:
            logging.error('Failed to list product ', e)
            abort(500, e)

