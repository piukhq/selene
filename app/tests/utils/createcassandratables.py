import cassandra
import settings

from bigdatalib.schema import Schema
from cassandralib.client import Client


# Utility file to create required cassandra tables in case of local docker cassandra container.
# This module is not needed to run Selene.

if __name__ == '__main__':
    client = Client(schema=Schema, hosts=settings.CASSANDRA_CLUSTER)
    tables = ['payment', 'invalid_payment', 'scheme', 'recent_transactions', 'reward',
              'scheme_information', 'real_time_transaction', 'join_status', 'file_logging']
    for table in tables:
        try:
            client.create_table(table)
        except cassandra.AlreadyExists:
            print('Skipping creation of {}, column family already exists.'.format(table))
        else:
            print('Created column family {}'.format(table))
