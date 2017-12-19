import os
from environment import read_env, env_var

read_env()

APP_DIR = os.path.abspath(os.path.dirname(__file__))

WRITE_FOLDER = env_var("WRITE_FOLDER", '/tmp/mids_output/')

TRANSACTION_MATCHING_FILES_CONFIG = ['sftp', 'amex', '192.168.1.13', 'amexsftp', 'am3xr00lz', 'inbox']

MAILGUN_URL = None  # 'https://api.mailgun.net/v3/uk.bink.com/messages'
MAILGUN_API_KEY = None  # 'key-63iepgmkm8qdzs0fxm05jy0oq3c1yd42'
MAILGUN_FROM_ADDRESS = None  # 'mids@uk.bink.com'

EMAIL_TARGETS = {
    'visa': None,  # 'mids@bink.com',
    'mastercard': None,  # 'mids@bink.com',
}

SQLALCHEMY_TRACK_MODIFICATIONS = False

SQLALCHEMY_DATABASE_URI = 'postgresql+psycopg2://{}:{}@{}:{}/{}'.format(
    env_var('PONTUS_USER', 'pontus'),
    env_var('PONTUS_PASSWORD', 'TJkD8GitA7NA'),
    env_var('PONTUS_HOST', '10.0.104.22'),
    env_var('PONTUS_PORT', '5432'),
    env_var('PONTUS_DATABASE', 'pontus')
)

SECRET_KEY = '3456hk3465hj345jh6jk456j45lk-0'
PROJECT_ROOT = os.path.abspath(os.path.join(APP_DIR, os.pardir))
DEBUG = env_var("SELENE_DEBUG", False)
TOKEN_SECRET = "8vA/fjVA83(n05LWh7R4'$3dWmVCU"

DEV_PORT = env_var('DEV_PORT', '5000')
DEV_HOST = env_var('DEV_HOST', '0.0.0.0')
