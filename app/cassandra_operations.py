import settings

from bigdatalib.schema import Schema
from cassandralib.client import Client

from app.utils import prepare_cassandra_file


class CassandraOperations:
    insert_table = 'scheme_information'
    columns = [
            'card_provider',
            'merchant_id',
            'scheme_provider',
            'merchant_name',
            'location',
            'postcode',
            'action'
    ]

    def __init__(self, file, merchant=None):
        self.client = Client(schema=Schema, hosts=settings.CASSANDRA_CLUSTER)

        if not file and not merchant:
            raise ValueError('cassandra input file or merchant name must be provided.')

        self.merchant = merchant
        self.rows = prepare_cassandra_file(file, self.columns) if file else None

    def run_operations(self):
        if self.merchant:
            self.remove_mids()

        else:
            action_sorted_rows = dict(A=list(), D=list(), U=list())

            for row in self.rows:
                action = row['action']
                del row['action']
                action_sorted_rows[action].append(row)

            if action_sorted_rows['A']:
                self.load_mids(action_sorted_rows['A'])

            if action_sorted_rows['D']:
                self.remove_mids(action_sorted_rows['D'])

    def load_mids(self, rows):
        self.client.insert(self.insert_table, rows)

    def remove_mids(self, rows=None):

        if self.merchant:
            raise NotImplementedError('delete by merchant')

        else:
            raise NotImplementedError('delete by cass_imp_file')
