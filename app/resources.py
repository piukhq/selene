from flask import request, jsonify
from flask_restful import Resource, Api
from app.import_mids import onboard_mids
from app.mastercard_handback import export_mastercard
from app.utils import wipe_output_folders

api = Api()


@api.resource('/mids/import_mids')
class ImportMids(Resource):
    @staticmethod
    def post():
        try:
            file = request.get_json()
            wipe_output_folders()
            onboard_mids(file, False, True)
            response = jsonify(success=True, error=None)

        except Exception as e:
            response = jsonify(success=False, error=str(e))
            response.status_code = 500

        return response


@api.resource('/mids/mastercard_handback')
class MastercardHandback(Resource):
    @staticmethod
    def post():
        try:
            file = request.get_json()
            export_mastercard(file)
            response = jsonify(success=True, error=None)

        except Exception as e:
            response = jsonify(success=False, error=str(e))
            response.status_code = 500

        return response
