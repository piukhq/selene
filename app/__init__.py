import logging

from ddtrace import tracer
from ddtrace.contrib.flask import TraceMiddleware

from flask import Flask
from flask_cdn import CDN
from flask_uploads import configure_uploads
from raven.contrib.flask import Sentry

from app.version import __version__
import settings
from app.views import bp, files

sentry = Sentry()
cdn = CDN()


def create_app(config_name='settings'):
    app = Flask(
        __name__,
        static_folder='static',
        static_url_path=settings.STATIC_URL
    )

    app.config.from_object(config_name)

    TraceMiddleware(
        app,
        tracer,
        service="selene",
        distributed_tracing=True)

    if settings.SENTRY_DSN:
        sentry.init_app(
            app,
            dsn=settings.SENTRY_DSN,
            logging=True,
            level=logging.ERROR)
        sentry.client.release = __version__

    cdn.init_app(app)

    app.register_blueprint(bp)
    configure_uploads(app, files)

    return app
