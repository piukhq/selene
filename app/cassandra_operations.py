import settings

from bigdatalib.schema import Schema
from cassandralib.client import Client

from app import sentry
from app.utils import prepare_cassandra_file


class CassandraOperations:
    client = Client(schema=Schema, hosts=settings.CASSANDRA_CLUSTER)
    insert_table = 'scheme_information'
    columns = [
            'card_provider',
            'merchant_id',
            'scheme_provider',
            'merchant_name',
            'location',
            'postcode',
            'created_date'
    ]

    def __init__(self, file):
        self.rows = prepare_cassandra_file(file, self.columns)

    def load_mids(self):
        try:
            self.client.insert(self.insert_table, self.rows)
            return False

        except Exception as e:
            sentry.captureException()
            return '{}: {}'.format(type(e).__name__, e)
