import json
from flask import make_response, request
from flask_restful import Resource, Api
from app.controller import onboard_mids
from app.utils import wipe_output_folders

api = Api()


@api.resource('/import_mids')
class ImportMids(Resource):
    @staticmethod
    def post():
        file = request.get_json()
        wipe_output_folders()
        onboard_mids(file, False, True)

        response = dict(success=True, processed_file=json.dumps(file))
        return make_response(json.dumps(response))
