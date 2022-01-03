import os
import json
import logging
import logging.config
import traceback

from flask import Flask, Blueprint, url_for
from flask_cors import CORS

from functools import wraps

import settings

logging_conf_path = os.path.normpath(os.path.join(os.path.dirname(__file__), 'logging.conf'))
logging.config.fileConfig(logging_conf_path)
log = logging.getLogger(__name__)


class PrefixMiddleware(object):

    def __init__(self, app, prefix=''):
        self.app = app
        self.prefix = prefix

    def __call__(self, environ, start_response):

        if environ['PATH_INFO'].startswith(self.prefix):
            environ['PATH_INFO'] = environ['PATH_INFO'][len(self.prefix):]
            environ['SCRIPT_NAME'] = self.prefix
            return self.app(environ, start_response)
        else:
            start_response('404', [('Content-Type', 'text/plain')])
            return ["This url does not belong to the app.".encode()]


app = Flask(__name__)
app.wsgi_app = PrefixMiddleware(app.wsgi_app, prefix=settings.BASE_PATH)
CORS(app)


def has_no_empty_params(rule):
    defaults = rule.defaults if rule.defaults is not None else ()
    arguments = rule.arguments if rule.arguments is not None else ()
    return len(defaults) >= len(arguments)


@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Strict-Transport-Security', 'max-age=31536000; includeSubDomains; preload;')
    response.headers.add('Content-Security-Policy',
                         "default-src 'self';"
                         "object-src 'none';"
                         "script-src 'self' 'unsafe-inline';"
                         "style-src 'self' 'unsafe-inline';"
                         "img-src 'self' data: blob:;")
    response.headers.add('X-Content-Type-Options', 'nosniff')
    response.headers.add('X-Frame-Options', 'SAMEORIGIN')
    response.headers.add('X-XSS-Protection', '1; mode=block')
    response.headers.add('Server', 'Undisclosed')

    return response

def configure_app(flask_app):
    flask_app.config['SERVER_URL'] = settings.SERVER_URL
    flask_app.config['SWAGGER_UI_DOC_EXPANSION'] = settings.RESTPLUS_SWAGGER_UI_DOC_EXPANSION
    flask_app.config['RESTPLUS_VALIDATE'] = settings.RESTPLUS_VALIDATE
    flask_app.config['RESTPLUS_MASK_SWAGGER'] = settings.RESTPLUS_MASK_SWAGGER
    flask_app.config['ERROR_404_HELP'] = settings.RESTPLUS_ERROR_404_HELP


def initialize_app(flask_app):
    configure_app(flask_app)

    blueprint = Blueprint('api', __name__, url_prefix='/api')
    CORS(blueprint)

    from api import api

    api.init_app(blueprint)

    from api.config import ns as ns_config
    api.add_namespace(ns_config)

    flask_app.register_blueprint(blueprint)

def main():
    initialize_app(app)
    
    app.run(debug=settings.DEBUG, host = settings.HOST, port = settings.PORT)


if __name__ == "__main__":
    main()

