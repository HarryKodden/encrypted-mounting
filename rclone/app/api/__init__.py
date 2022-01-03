import logging
import traceback

from flask import url_for, request
from flask_restplus import Api

from functools import wraps

import settings

log = logging.getLogger(__name__)

authorizations = {
    'apikey': {
        'type': 'apiKey',
        'in': 'header',
        'name': 'X-API-KEY'
    }
}

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):

        token = None 

        if settings.API_KEY in request.headers:
            token = request.headers[settings.API_KEY]
        
        if not token:
            return {'message': 'API-KEY is missing.' }, 401
        
        log.debug('API_KEY: {}'.format(token))

        return f(*args, **kwargs)

    return decorated

def remote_user_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):

        if 'Remote-User' not in request.headers:
            return {'message': 'User not authenticated' }, 401
        
        return f(*args, **kwargs)

    return decorated


class MyApi(Api):
    @property
    def specs_url(self):
        """Monkey patch for HTTPS"""
        scheme = 'https' if settings.SERVER_URL.startswith("https://") else 'http'
        return url_for(self.endpoint('specs'), _external=True, _scheme=scheme)


api = MyApi(doc='/doc/',
        version=settings.API_VERSION, 
        title=settings.API_TITLE,
        description=settings.API_DESCRIPTION,
        authorizations=authorizations
)


@api.errorhandler
def default_error_handler(e):
    message = 'An unhandled exception occurred.'
    log.exception(message)

    if not settings.DEBUG:
        return {'message': message}, 500
