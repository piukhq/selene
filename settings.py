import os

from environment import read_env, env_var

APP_DIR = os.path.abspath(os.path.dirname(__file__))
SECRET_KEY = '3456hk3465hj345jh6jk456j45lk-0'
PROJECT_ROOT = os.path.abspath(os.path.join(APP_DIR, os.pardir))

read_env()

WRITE_FOLDER = env_var("WRITE_FOLDER", '/tmp/mids_output/')

SQLALCHEMY_TRACK_MODIFICATIONS = False
SQLALCHEMY_DATABASE_URI = 'postgresql+psycopg2://{user}:{password}@{host}:{port}/{database}'.format(
    user=env_var('PONTUS_USER', 'pontus'),
    password=env_var('PONTUS_PASSWORD', 'TJkD8GitA7NA'),
    host=env_var('PONTUS_HOST', '10.0.104.22'),
    port=env_var('PONTUS_PORT', '5432'),
    database=env_var('PONTUS_DATABASE', 'pontus')
)

SENTRY_DSN = env_var("SELENE_SENTRY_DSN")
DEBUG = env_var("SELENE_DEBUG", False)
DEV_PORT = env_var('DEV_PORT', '8000')
DEV_HOST = env_var('DEV_HOST', '0.0.0.0')
SERVICE_TOKEN = 'Wvp*F3}<aQCAul=l]gjHu!/TD+_x=Sx8'

STATIC_URL = env_var('SELENE_STATIC_URL', '/static')
UPLOADED_FILES_DEST = os.path.join(STATIC_URL, 'files')

AZURE_ACCOUNT_NAME = env_var('AZURE_ACCOUNT_NAME', 'bink')
AZURE_ACCOUNT_KEY = env_var('AZURE_ACCOUNT_KEY',
                            'xaeP9dmuYEWf/gthvteUj2utPcIM/B4dPRPoyHAd22LEI/6l/XJhYnzu2I66rI7PEdgoyvvDKJNYcmxd9vsLhA==')

CDN_DOMAIN = env_var('CDN_DOMAIN')
CDN_DEBUG = False
CDN_TIMESTAMP = False
CDN_HTTPS = True
