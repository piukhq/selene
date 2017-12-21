from flask import Flask
from app.models import db
from app.utils import init_folders


def create_app(config_name='settings'):
    from app.resources import api

    init_folders()

    app = Flask('main')
    app.config.from_object(config_name)
    db.init_app(app)
    api.init_app(app)

    return app
