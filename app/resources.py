import json
from flask import make_response, request
from flask_restful import Resource, Api

api = Api()


@api.resource('/test')
class ImportMids(Resource):
    @staticmethod
    def post():

        result = request.get_json()
        return make_response(json.dumps(result))
