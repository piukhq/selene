import settings

from flask import request, jsonify
from flask_restful import Resource, Api
from functools import wraps

from app import sentry
from app.import_mids import onboard_mids
from app.mastercard_handback import export_mastercard
from app.handback_duplicates import find_duplicate_mids_in_mastercard_handback_file
from app.cassandra_operations import CassandraOperations
from app.utils import wipe_output_folders


def handle_exceptions(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            return f(*args, **kwargs)

        except Exception as e:
            if settings.USE_SENTRY:
                sentry.captureException()

            error = '{}: {}'.format(type(e).__name__, e)
            response = jsonify(success=False, error=error)
            response.status_code = 500
            return response

    return decorated_function


api = Api(decorators=[handle_exceptions])


def token_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.headers.get('Authorization')
        if token != settings.SERVICE_TOKEN:
            response = jsonify(success=False, error='Wrong token')
            response.status_code = 401
            return response

        return f(*args, **kwargs)

    return decorated_function


@api.resource('/mids/import_mids')
class ImportMids(Resource):
    @staticmethod
    def post():
        file = request.get_json()
        folder_name = onboard_mids(file, False, True)
        return jsonify(success=True, error=None, folder_name=folder_name)


@api.resource('/mids/mastercard_handback')
class MastercardHandback(Resource):
    @staticmethod
    def post():
        file = request.get_json()
        export_mastercard(file)
        return jsonify(success=True, error=None, folder_name='handback')


@api.resource('/mids/handback_duplicates')
class FindDuplicatesInHandback(Resource):
    @staticmethod
    def post():
        file = request.get_json()
        find_duplicate_mids_in_mastercard_handback_file(file)
        return jsonify(success=True, error=None, folder_name='duplicates')


@api.resource('/mids/wipe_folders')
class WipeOutputFolders(Resource):
    @staticmethod
    def get():
        wipe_output_folders()
        return jsonify(success=True, error=None)


@api.resource('/mids/cassandra')
class CassandraDatabaseOperations(Resource):
    @staticmethod
    @token_required
    def post():
        received = request.get_json()
        if 'merchant' in received:
            merchant, file = received.get('merchant'), None

        else:
            merchant, file = None, received

        CassandraOperations(file=file, merchant=merchant).run_operations()
        return jsonify(success=True, error=None)


@api.resource('/mids/cassandra/providers')
class CassandraSchemeProviders(Resource):
    @staticmethod
    def get():
        result = CassandraOperations().get_providers_list()
        return jsonify(success=True, error=None, merchants=result)
