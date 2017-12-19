import os
import settings

from flask import Flask
from app.models import db


def create_app(config_name='settings'):
    from app.resources import api

    path = os.path.join(settings.WRITE_FOLDER, 'merchants')

    os.makedirs(path, exist_ok=True)
    os.makedirs(path + '/visa', exist_ok=True)
    os.makedirs(path + '/amex', exist_ok=True)
    os.makedirs(path + '/mastercard', exist_ok=True)

    app = Flask('main')
    app.config.from_object(config_name)
    db.init_app(app)
    api.init_app(app)

    return app
