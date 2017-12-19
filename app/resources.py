import os
import shutil
import settings

from flask import request, jsonify
from flask_restful import Resource, Api

from app.import_mids import onboard_mids
from app.mastercard_handback import export_mastercard
from app.handback_duplicates import find_duplicate_mids_in_mastercard_handback_file
from app.utils import wipe_output_folders, csv_to_list_json

api = Api()


@api.resource('/mids/import_mids')
class ImportMids(Resource):
    @staticmethod
    def post():
        try:
            file = request.get_json()
            folder_name = onboard_mids(file, False, True)
            response = jsonify(success=True, error=None, folder_name=folder_name)

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


@api.resource('/mids/handback_duplicates')
class FindDuplicatesInHandback(Resource):
    @staticmethod
    def post():
        try:
            file = request.get_json()
            find_duplicate_mids_in_mastercard_handback_file(file)
            response = jsonify(success=True, error=None)

        except Exception as e:
            response = jsonify(success=False, error=str(e))
            response.status_code = 500

        return response


@api.resource('/mids/wipe_folders')
class WipeOutputFolders(Resource):
    @staticmethod
    def get():
        try:
            wipe_output_folders()
            response = jsonify(success=True, error=None)

        except Exception as e:
            response = jsonify(success=False, error=str(e))
        return response


@api.resource('/csv_to_json')
class CsvToJson(Resource):
    @staticmethod
    def post():
        try:
            file = request.files.get('file')
            path = os.path.join(settings.WRITE_FOLDER, 'convert')
            file_path = os.path.join(path, 'input.csv')
            os.makedirs(path, exist_ok=True)
            file.save(file_path)

            result = csv_to_list_json(file_path)
            shutil.rmtree(path)

            response = jsonify(success=True, error=None, result=result)

        except Exception as e:
            response = jsonify(success=False, error=str(e))
            response.status_code = 500

        return response
