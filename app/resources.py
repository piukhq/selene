from flask import request, jsonify
from flask_restful import Resource, Api
from app.onboard_mids import onboard_mids
from app.utils import wipe_output_folders, format_json_input

api = Api()


@api.resource('/mids/import_mids')
class ImportMids(Resource):
    @staticmethod
    def post():
        file = request.get_json()
        wipe_output_folders()
        onboard_mids(file, False, True)
        file = format_json_input(file)
        response = dict(success=True, processed_file=file)
        return jsonify(response)


@api.resource('/mids/mastercard_handback')
class MastercardHandback(Resource):
    @staticmethod
    def post():
        pass
