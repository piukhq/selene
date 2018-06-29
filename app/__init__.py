import logging

from flask import Flask
from raven.contrib.flask import Sentry

from app.version import __version__
from app.utils import init_folders
from app.models import db
import settings

sentry = Sentry()


def create_app(config_name='settings'):
    from app.resources import api

    init_folders()

    app = Flask('main')
    app.config.from_object(config_name)

    if settings.SENTRY_DSN:
        sentry.init_app(
            app,
            dsn=settings.SENTRY_DSN,
            logging=True,
            level=logging.ERROR)
        sentry.client.release = __version__

    db.init_app(app)
    api.init_app(app)

    return app
