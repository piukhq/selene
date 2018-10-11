import logging

from flask import Flask
from flask_uploads import configure_uploads
from raven.contrib.flask import Sentry

from app.version import __version__
from app.models import db
import settings
from app.views import bp, files

sentry = Sentry()


def create_app(config_name='settings'):
    app = Flask(__name__)
    app.config.from_object(config_name)

    if settings.SENTRY_DSN:
        sentry.init_app(
            app,
            dsn=settings.SENTRY_DSN,
            logging=True,
            level=logging.ERROR)
        sentry.client.release = __version__

    db.init_app(app)
    app.register_blueprint(bp)
    configure_uploads(app, files)

    return app
