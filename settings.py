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
    # ('sftp', 'amex', 'fsgateway.aexp.com', 'CHINGSPRD', 'taua@13', 'inbox'),
    'sftp', 'amex', '192.168.1.13', 'amexsftp', 'am3xr00lz', 'inbox',
]

MAILGUN_URL = 'https://api.mailgun.net/v3/uk.bink.com/messages'
MAILGUN_API_KEY = 'key-63iepgmkm8qdzs0fxm05jy0oq3c1yd42'
MAILGUN_FROM_ADDRESS = 'mids@uk.bink.com'

EMAIL_TARGETS = {
    # merchant : email address
    'visa': 'mids@bink.com',
    'mastercard': 'mids@bink.com',
}
