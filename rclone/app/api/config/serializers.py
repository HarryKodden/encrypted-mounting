from flask_restplus import fields
from api import api

service = api.model('service', {
    'service': fields.String(readOnly=True, description='The name of a service')
})

