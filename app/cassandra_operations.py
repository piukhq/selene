import settings

from bigdatalib.schema import Schema
from cassandralib.client import Client

from app.utils import prepare_cassandra_file


def execute_patched(self, statement):
    """
    Override Client execute method to return query result.
    :param self: Client object
    :param statement: query to be executed
    :return: query result
    """
    return self.session.execute(statement)


class CassandraOperations:
    keyspace = 'lakeyspace'
    insert_table = 'scheme_information'
    columns = ('card_provider', 'merchant_id', 'scheme_provider', 'merchant_name', 'location', 'postcode', 'action')

    select_query = "select * from %s.%s where %s='{}';" % (keyspace, insert_table, columns[2])
    delete_query = "delete from %(ks)s.%(t)s where %(f1)s='{%(f1)s}' and %(f2)s='{%(f2)s}';" % \
                   {'ks': keyspace, 't': insert_table, 'f1': columns[0], 'f2': columns[1]}

    def __init__(self, file, merchant=None):
        Client.execute = execute_patched
        self.client = Client(schema=Schema, hosts=settings.CASSANDRA_CLUSTER)

        if not file and not merchant:
            raise ValueError('cassandra input file or merchant name must be provided.')

        self.merchant = merchant
        self.rows = prepare_cassandra_file(file, self.columns) if file else None

    def select_by_provider(self):
        result = self.client.execute(self.select_query.format(self.merchant))
        self.merchant = None
        self.remove_mids(result.current_rows)

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
            self.select_by_provider()

        else:
            for row in rows:
                self.client.execute(self.delete_query.format(**row))
