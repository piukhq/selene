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
    #('sftp', 'amex', 'fsgateway.aexp.com', 'CHINGSPRD', 'taua@13', 'inbox'),
    'sftp', 'amex', '192.168.1.13', 'amexsftp', 'am3xr00lz', 'inbox',
]

EMAIL_SOURCE_CONFIG = [
    # user | password | host | port
    'mids@bink.com', '=Yg4CaG@6K', 'mail.bink.com', 25,
]

EMAIL_TARGETS = {
    # merchant : email address
    'visa': 'mids@bink.com',
    'mastercard': 'mids@bink.com',
}

