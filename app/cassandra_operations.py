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
            return str(e)


def load_mids_to_cassandra(file):
    cassandra = CassandraOperations()
    rows = prepare_cassandra_file(file, cassandra.columns)

    try:
        cassandra.load_row(rows)
        error = None

    except Exception as e:
        error = str(e)

    return error
