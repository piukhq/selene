import settings

from flask import request
from flask_restplus import Resource, Api, abort
from functools import wraps

from app.import_mids import onboard_mids
from app.mastercard_handback import export_mastercard
from app.handback_duplicates import find_duplicate_mids_in_mastercard_handback_file
from app.cassandra_operations import CassandraOperations
from app.utils import wipe_output_folders

api = Api()


@api.errorhandler
def handle_exceptions(e):
    message = '{}: {}'.format(type(e).__name__, e)
    return dict(success=False, message=message)


def token_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.headers.get('Authorization')
        if token != settings.SERVICE_TOKEN:
            abort(401, 'AuthToken: Authorization token missing or incorrect.', success=False)

        return f(*args, **kwargs)

    return decorated_function


@api.route('/mids/import_mids', endpoint='import_mids')
class ImportMids(Resource):
    @staticmethod
    def post():
        file = request.get_json()
        folder_name = onboard_mids(file, False, True)
        return dict(success=True, folder_name=folder_name)


@api.route('/mids/mastercard_handback', endpoint='mastercard_handback')
class MastercardHandback(Resource):
    @staticmethod
    def post():
        file = request.get_json()
        export_mastercard(file)
        return dict(success=True, folder_name='handback')


@api.route('/mids/handback_duplicates', endpoint='handback_duplicates')
class FindDuplicatesInHandback(Resource):
    @staticmethod
    def post():
        file = request.get_json()
        find_duplicate_mids_in_mastercard_handback_file(file)
        return dict(success=True, folder_name='duplicates')


@api.route('/mids/wipe_folders', endpoint='wipe_folders')
class WipeOutputFolders(Resource):
    @staticmethod
    def get():
        wipe_output_folders()
        return dict(success=True)


@api.route('/mids/cassandra', endpoint='cassandra_ops')
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
        return dict(success=True)


@api.route('/mids/cassandra/providers', endpoint='get_providers')
class CassandraSchemeProviders(Resource):
    @staticmethod
    def get():
        result = CassandraOperations().get_providers_list()
        return dict(success=True, merchants=result)
