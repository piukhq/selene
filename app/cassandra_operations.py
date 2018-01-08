import settings

from bigdatalib.schema import Schema
from cassandralib.client import Client

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

    def load_row(self, row):
        try:
            self.client.insert(self.insert_table, row)
            return False

        except Exception as e:
            return '{}: {}'.format(type(e).__name__, e)


def load_mids_to_cassandra(file):
    cassandra = CassandraOperations()
    try:
        rows = prepare_cassandra_file(file, cassandra.columns)
        return cassandra.load_row(rows)

    except ValueError as e:
        return 'ValueError: {}'.format(e)
