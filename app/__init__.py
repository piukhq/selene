import logging
import settings

from flask import Flask
from raven.contrib.flask import Sentry
from app.models import db
from app.utils import init_folders

sentry = Sentry()


def create_app(config_name='settings'):
    from app.resources import api

    init_folders()

    app = Flask('main')
    app.config.from_object(config_name)

    if settings.USE_SENTRY:
        sentry.init_app(app, dsn=settings.SENTRY_DSN, logging=True, level=logging.ERROR)

    db.init_app(app)
    api.init_app(app)

    return app