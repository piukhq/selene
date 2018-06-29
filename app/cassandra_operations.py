import settings
import requests
import arrow

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

    get_providers_query = "select %s from %s.%s;" % (columns[2], keyspace, insert_table)
    select_by_provider_query = "select * from %s.%s where %s='{}';" % (keyspace, insert_table, columns[2])
    delete_query = "delete from %(ks)s.%(t)s where %(f1)s='{%(f1)s}' and %(f2)s='{%(f2)s}';" % \
                   {'ks': keyspace, 't': insert_table, 'f1': columns[0], 'f2': columns[1]}

    def __init__(self, user=None, file=None, merchant=None):
        Client.execute = execute_patched
        if user:
            self.user_id = str(user['id'])
            self.user_name = str(user['name'])

        self.client = Client(schema=Schema, hosts=settings.CASSANDRA_CLUSTER)
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

    def get_providers_list(self):
        result = self.client.execute(self.get_providers_query)
        providers = {row[self.columns[2]] for row in result}
        return list(providers)

    def select_by_provider(self):
        result = self.client.execute(self.select_by_provider_query.format(self.merchant))
        if result.current_rows:
            self.remove_mids(result)

    def load_mids(self, rows):
        self.client.insert(self.insert_table, rows)
        self.send_audit('A', rows)

    def remove_mids(self, rows=None):
        if rows:
            for row in rows:
                self.client.execute(self.delete_query.format(**row))

            self.send_audit('D', rows)

        else:
            self.select_by_provider()

    def send_audit(self, action, rows):
        if not settings.EREBUS_URL:
            return None

        affected_rows = list()
        for row in rows:
            document = dict(user_name=self.user_name, user_id=self.user_id, action=action)
            document.update(**row)

            if document.get('created_date'):
                document['when'] = arrow.get(document.pop('created_date')).format()

            else:
                document['when'] = arrow.utcnow().format()

            affected_rows.append(document)

        requests.post(settings.EREBUS_URL, json=affected_rows)
