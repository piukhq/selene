import os
from environment import read_env, env_var

read_env()

APP_DIR = os.path.abspath(os.path.dirname(__file__))

# dev machine
CASSANDRA_CLUSTER = ('192.168.1.60', '192.168.1.61',  '192.168.1.62')

# local machine
# CASSANDRA_CLUSTER = ('127.0.0.1', '127.0.0.2', '127.0.0.3')


CASSANDRA_TRANSACTION_KEYSPACE = 'lakeyspace'

TRANSACTION_MATCHING_FILES_CONFIG = [
    # 'sftp', 'amex', 'fsgateway.aexp.com', 'CHINGSPRD', 'taua@13', 'inbox',
    'sftp', 'amex', '192.168.1.13', 'amexsftp', 'am3xr00lz', 'inbox',
]

MAILGUN_URL = 'https://api.mailgun.net/v3/uk.bink.com/messages'
MAILGUN_API_KEY = 'key-63iepgmkm8qdzs0fxm05jy0oq3c1yd42'
MAILGUN_FROM_ADDRESS = 'mids@uk.bink.com'

EMAIL_TARGETS = {
    'visa': 'mids@bink.com',
    'mastercard': 'mids@bink.com',
}

ASK_TO_SEND_MAIL = env_var('ASK_TO_SEND_MAIL', True)
ASK_POSTCODE_VALIDATION = env_var('ASK_POSTCODE_VALIDATION', True)
