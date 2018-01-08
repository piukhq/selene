import cassandra
import settings

from bigdatalib.schema import Schema
from cassandralib.client import Client


class CassandraClient:
    client = Client(schema=Schema, hosts=settings.CASSANDRA_CLUSTER)

    def load_row_to_cassandra(self):
        table_name = 'scheme_information'
        pass
