import os
import re

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

CASSANDRA_CLUSTER = env_var('CASSANDRA_CLUSTER', '10.0.104.30, 10.0.104.31, 10.0.104.32').split(', ')

SENTRY_DSN = env_var("SELENE_SENTRY_DSN", None)
USE_SENTRY = env_var("USE_SENTRY", True if SENTRY_DSN else False)
SECRET_KEY = '3456hk3465hj345jh6jk456j45lk-0'
PROJECT_ROOT = os.path.abspath(os.path.join(APP_DIR, os.pardir))
DEBUG = env_var("SELENE_DEBUG", False)
DEV_PORT = env_var('DEV_PORT', '8000')
DEV_HOST = env_var('DEV_HOST', '0.0.0.0')
SERVICE_TOKEN = 'Wvp*F3}<aQCAul=l]gjHu!/TD+_x=Sx8'

AMEX_SFTP_CONFIG = ['fsgatewaytest.aexp.com', 'CHINGSTST', 'Talu@6713', 'inbox']

EMAIL_USERNAME = env_var('EMAIL_USERNAME', 'itapps@bink.com')
EMAIL_PASSWORD = env_var('EMAIL_PASSWORD', '$NickCisEcbeu1')
EMAIL_HOST = env_var('EMAIL_HOST', 'smtp.office365.com')
EMAIL_PORT = env_var('EMAIL_PORT', 587)
EMAIL_TARGETS = {
    'visa': env_var('VISA_MAIL', 'mids@bink.com'),
    'mastercard': env_var('MASTERCARD_MAIL', 'mids@bink.com')
}

GET_ATTACHMENT = {
    'visa': re.compile('^CAID_\\w+_LoyaltyAngels_[0-9]{8}.xlsx$'),
    'amex': re.compile('\\w+_AXP_MER_REG_[0-9]{8}_[0-9]{6}.txt$')
}
