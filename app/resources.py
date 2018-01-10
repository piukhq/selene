from flask import request, jsonify
from flask_restful import Resource, Api

from app import sentry
from app.import_mids import onboard_mids
from app.mastercard_handback import export_mastercard
from app.handback_duplicates import find_duplicate_mids_in_mastercard_handback_file
from app.cassandra_operations import CassandraOperations
from app.utils import wipe_output_folders

api = Api()


def handle_exception(e):
    sentry.captureException()
    error = '{}: {}'.format(type(e).__name__, e)
    response = jsonify(success=False, error=error)
    response.status_code = 500
    return response


@api.resource('/mids/import_mids')
class ImportMids(Resource):
    @staticmethod
    def post():
        try:
            file = request.get_json()
            folder_name = onboard_mids(file, False, True)
            response = jsonify(success=True, error=None, folder_name=folder_name)

        except Exception as e:
            response = handle_exception(e)

        return response


@api.resource('/mids/mastercard_handback')
class MastercardHandback(Resource):
    @staticmethod
    def post():
        try:
            file = request.get_json()
            export_mastercard(file)
            response = jsonify(success=True, error=None, folder_name='handback')

        except Exception as e:
            response = handle_exception(e)

        return response


@api.resource('/mids/handback_duplicates')
class FindDuplicatesInHandback(Resource):
    @staticmethod
    def post():
        try:
            file = request.get_json()
            find_duplicate_mids_in_mastercard_handback_file(file)
            response = jsonify(success=True, error=None, folder_name='duplicates')

        except Exception as e:
            response = handle_exception(e)

        return response


@api.resource('/mids/wipe_folders')
class WipeOutputFolders(Resource):
    @staticmethod
    def get():
        try:
            wipe_output_folders()
            response = jsonify(success=True, error=None)

        except Exception as e:
            response = handle_exception(e)

        return response


@api.resource('/mids/cassandra')
class CassandraDatabaseOperations(Resource):
    @staticmethod
    def post():
        try:
            received = request.get_json()
            if 'merchant' in received:
                merchant, file = received.get('merchant'), None

            else:
                merchant, file = None, received

            CassandraOperations(file=file, merchant=merchant).run_operations()
            response = jsonify(success=True, error=None)

        except Exception as e:
            response = handle_exception(e)

        return response
