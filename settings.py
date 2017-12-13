import os
from environment import read_env, env_var

read_env()

APP_DIR = os.path.abspath(os.path.dirname(__file__))

WRITE_FOLDER = env_var("WRITE_FOLDER", APP_DIR)

CASSANDRA_CLUSTER = ('192.168.1.60', '192.168.1.61',  '192.168.1.62')

CASSANDRA_TRANSACTION_KEYSPACE = 'lakeyspace'

TRANSACTION_MATCHING_FILES_CONFIG = ['sftp', 'amex', '192.168.1.13', 'amexsftp', 'am3xr00lz', 'inbox']

MAILGUN_URL = None  # 'https://api.mailgun.net/v3/uk.bink.com/messages'
MAILGUN_API_KEY = None  # 'key-63iepgmkm8qdzs0fxm05jy0oq3c1yd42'
MAILGUN_FROM_ADDRESS = None  # 'mids@uk.bink.com'

EMAIL_TARGETS = {
    'visa': 'mids@bink.com',
    'mastercard': 'mids@bink.com',
}

ASK_TO_SEND_MAIL = env_var('ASK_TO_SEND_MAIL', True)
ASK_POSTCODE_VALIDATION = env_var('ASK_POSTCODE_VALIDATION', True)

SECRET_KEY = '3456hk3465hj345jh6jk456j45lk-0'
PROJECT_ROOT = os.path.abspath(os.path.join(APP_DIR, os.pardir))
DEBUG = env_var("SELENE_DEBUG", True)
TOKEN_SECRET = "8vA/fjVA83(n05LWh7R4'$3dWmVCU"

DEV_PORT = env_var('DEV_PORT', '5000')
DEV_HOST = env_var('DEV_HOST', '0.0.0.0')
