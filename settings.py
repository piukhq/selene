import os
from environment import read_env, env_var

read_env()

APP_DIR = os.path.abspath(os.path.dirname(__file__))
WRITE_FOLDER = env_var("WRITE_FOLDER", '/tmp/mids_output/')

SQLALCHEMY_TRACK_MODIFICATIONS = False
SQLALCHEMY_DATABASE_URI = 'postgresql+psycopg2://{user}:{password}@{host}:{port}/{database}'.format(
    user=env_var('PONTUS_USER', 'pontus'),
    password=env_var('PONTUS_PASSWORD', 'TJkD8GitA7NA'),
    host=env_var('PONTUS_HOST', '10.0.104.22'),
    port=env_var('PONTUS_PORT', '5432'),
    database=env_var('PONTUS_DATABASE', 'pontus')
)

SECRET_KEY = '3456hk3465hj345jh6jk456j45lk-0'
PROJECT_ROOT = os.path.abspath(os.path.join(APP_DIR, os.pardir))
DEBUG = env_var("SELENE_DEBUG", False)
TOKEN_SECRET = "8vA/fjVA83(n05LWh7R4'$3dWmVCU"
DEV_PORT = env_var('DEV_PORT', '8000')
DEV_HOST = env_var('DEV_HOST', '0.0.0.0')

TRANSACTION_MATCHING_FILES_CONFIG = ['sftp', 'amex', '192.168.1.13', 'amexsftp', 'am3xr00lz', 'inbox']

EMAIL_USERNAME = env_var('EMAIL_USERNAME', 'itapps@bink.com')
EMAIL_PASSWORD = env_var('EMAIL_PASSWORD', '$NickCisEcbeu1')
EMAIL_HOST = env_var('EMAIL_HOST', 'smtp.office365.com')
EMAIL_PORT = env_var('EMAIL_PORT', 587)
EMAIL_TARGETS = {
    'visa': env_var('VISA_MAIL', 'mids@bink.com'),
    'mastercard': env_var('MASTERCARD_MAIL', 'mids@bink.com')
}
