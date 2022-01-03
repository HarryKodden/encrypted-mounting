import os
import logging
import settings
import werkzeug
import uuid

from flask import request, send_from_directory
from flask_restplus import Resource, fields, reqparse

from api import api, token_required, remote_user_required

from vault import rClone

log = logging.getLogger(__name__)

ns = api.namespace('config', description='Operations related to services')

my_rclone = rClone()

file_upload = reqparse.RequestParser()
file_upload.add_argument('rclone_config_file',  
                         type=werkzeug.datastructures.FileStorage, 
                         location='files', 
                         required=True, 
                         help='Config file')


@ns.route('/dump')
class Config(Resource):

    def post(self):
        """
        dump config from Vault
        """
        return my_rclone.get_config(settings.RCLONE_ADMIN_CONFIG)


mount_config = api.model('mount_config', {
    'config': fields.Raw(required=True, description='Mount config')
})


@ns.route('/mount/<string:mount>')
@api.response(404, 'mount not found.')
class Mount(Resource):

    def get(self, mount):
        """
        Returns details for a given user for a given mount.
        """
        try:
            return my_rclone.read(mount)
        except:
            return {}


    @api.expect(mount_config)
    def post(self, mount, payload = None):
        """
        Create/Updates details for a given user for a given mount.
        """
        if not payload:
            payload = api.payload

        my_rclone.write(mount, payload['config'])

        return {}

    def delete(self, mount):
        """
        delete a given mount
        """

        my_rclone.delete(mount)

        return {}


mount_name = api.model('mount_name', {
    'name': fields.String(required=True, description='Mount Name')
})

mount_type_parameters = api.model('mount_type_parameters', {
    'name': fields.String(required=True, description='Mount Name'),
    'type': fields.String(required=True, description='Mount Type'),
    'parameters': fields.Raw(required=True, description='Mount Parameters')
})

mount_parameters = api.model('mount_parameters', {
    'name': fields.String(required=True, description='Mount Name'),
    'parameters': fields.Raw(required=True, description='Mount Parameters')
})

@ns.route('/get', methods=['POST'])
class get(Mount):

    @api.expect(mount_name)
    def post(self):
        """
        Read a mount.
        """

        return self.get(api.payload['name'])

@ns.route('/create', methods=['POST'])
class create(Mount):

    @api.expect(mount_type_parameters)
    def post(self):
        """
        Create a mount.
        """

        mount  = api.payload['name']
        config = api.payload['parameters']
        config['type'] = api.payload['type']

        return super().post(mount, payload={ 'config' : config })

@ns.route('/update', methods=['POST'])
class update(Mount):

    @api.expect(mount_parameters)
    def post(self):
        """
        Update a mount.
        """

        mount  = api.payload['name']
        config = api.payload['parameters']

        return super().post(mount, payload={ 'config' : config })

@ns.route('/delete', methods=['POST'])
class delete(Mount):

    @api.expect(mount_name)
    def post(self):
        """
        Delete a mount.
        """

        return self.delete(api.payload['name'])

@ns.route('/listremotes',methods=['POST'])
class ListRemotes(Config):

    def post(self):
        """
        list remotes
        """
        return { "remotes": list(super().post().keys()) }

@ns.route('/export',methods=['GET'])
class Export(Config):

    def get(self):
        """
        export rclone configution file
        """
        try:
            # During export there is no concern for race condition, so just name it /tmp/rclone.conf
            dir = '/tmp'
            file = 'rclone.conf'
            my_rclone.get_config(dir+'/'+file)
            return send_from_directory(dir, file, as_attachment=True)
        except Exception as e:
            return str(e), 401
        finally:
            os.remove(dir+'/'+file)

@ns.route('/import', methods=['POST'])
class Import(Config):

    @api.expect(file_upload)
    def post(self):
        """
        import rclone configution file
        """
        args = file_upload.parse_args()

        try:
            # During import, we could have race condition, therefor make filename usinque !
            dir = '/tmp'
            file = str(uuid.uuid4())
            args['rclone_config_file'].save(dir+'/'+file)
            my_rclone.put_config(dir+'/'+file)
        except Exception as e:
            return str(e), 401
        finally:
            os.remove(dir+'/'+file)

        return "OK !"
