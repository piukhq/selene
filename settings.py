import os

APP_DIR = os.path.abspath(os.path.dirname(__file__))

# -------------------------------------------------------------------------------
# Cassandra cluster
# -------------------------------------------------------------------------------

# dev machine
CASSANDRA_CLUSTER = ('192.168.1.60', '192.168.1.61',  '192.168.1.62')
# local machine
# CASSANDRA_CLUSTER = ('127.0.0.1', '127.0.0.2', '127.0.0.3')
# aws deployment
# CASSANDRA_CLUSTER=(['unknown', 'unknown', 'unknown')

CASSANDRA_TRANSACTION_KEYSPACE = 'lakeyspace'

TRANSACTION_MATCHING_FILES_CONFIG = [
    # sftp | slug | URL | username | password | dest
    ('sftp', 'amex', 'fsgateway.aexp.com', 'CHINGSPRD', 'taua@13', 'inbox'),
]