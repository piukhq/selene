from flask import request, send_from_directory, jsonify
from flask_restful import Resource, Api
from app.controller import onboard_mids
from app.utils import wipe_output_folders, format_json_input
from settings import APP_DIR

api = Api()


@api.resource('/import_mids')
class ImportMids(Resource):
    @staticmethod
    def post():
        file = request.get_json()
        wipe_output_folders()
        onboard_mids(file, False, True)
        file = format_json_input(file)
        response = dict(success=True, processed_file=file)
        return jsonify(response)


@api.resource('/<filename>')
class OutputFolders(Resource):
    @staticmethod
    def get(filename):
        return send_from_directory(APP_DIR + "/app/tests/unit/fixture/", filename)
