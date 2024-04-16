import os
import io
import json
import uuid
import logging
import settings
import subprocess
import configparser
import socket
import hashlib

from contextlib import closing
from requests import request

log = logging.getLogger(__name__)

def pretty(data):
    try:
        return json.dumps(json.loads(data), sort_keys=True, indent=4)
    except:
        return data

def find_free_port():
    with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as s:
        s.bind(('', 0))
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        return s.getsockname()[1]

class Vault(object):

    def __init__(self):
        self.token = None
        
    def headers(self):

        if self.token:
            # Check token is still valid...
            (rc, _) = self.api(
                "/v1/sys/auth",
                headers={ "X-Vault-Token": self.token }
            )

            if rc == 403:
                self.token = None

        if not self.token:
            # Authenticate...
            (rc, data) = self.api(
                "/v1/auth/userpass/login/{}".format(settings.VAULT_USER),
                method="POST",
                payload={ "password": settings.VAULT_PASS },
                headers={ "Content-Type": "application/json" }
            )

            if rc == 200:
                self.token = json.loads(data)['auth']['client_token']

        if not self.token:
            raise Exception("Can not connect to Vault !")

        return {
            "X-Vault-Token": self.token,
            "Content-Type": "application/json"
        }

    def api(self, uri, method="GET", payload={}, headers=None):

        if not headers:
            headers = self.headers()

        url = "{}{}".format(settings.VAULT_ADDR, uri)
        log.debug("[VAULT] URL: {}".format(url))
        
        if payload:
            log.debug("[VAULT] DATA: {}".format(pretty(payload)))

        response = request(method, url, json=payload, headers=headers)

        log.debug(pretty(response.text))
        
        return response.status_code, response.text

def run(cmd):

    log.debug("Executing command: '{}'...".format(cmd))

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.stdout > '':
        log.debug("{}:\n*** TOP OF STDOUT ***\n{}*** END OF STDOUT ***".format(cmd, result.stdout))
    if result.stderr > '' and not result.stderr.startswith('Warning'):
        raise Exception(result.stderr)

    return result.stdout

def pipe(cmds):
    pipes = []
    p = None

    for cmd in cmds:
        log.info('Pipe cmd: {}'.format(cmd))

        if p:
            p = subprocess.Popen(cmd, stdin = p.stdout, stdout=subprocess.PIPE)
        else:
            p = subprocess.Popen(cmd, stdout=subprocess.PIPE)

        pipes.append(p)

    if len(pipes) == 0:
        raise Exception("Empty pipe...")

    # Close intermediate stdouts...
    for i in range(len(pipes)-2):
        pipes[i].stdout.close()

    out, err = pipes[len(pipes)-1].communicate()
    if err:
        raise Exception(err)
    
    return out.decode()

def spawn(cmd):
    subprocess.Popen(cmd, start_new_session=True)
        
class rClone(Vault):

    def __init__(self):
        super().__init__()
        self.start()

    def mounts(self):
        log.info("[MOUNTS]...")

        result = {}

        (rc, data) = self.api(
            "/v1/secret/metadata/mounts",
            method="LIST"
        )
        
        if rc == 200:
            for name in json.loads(data)['data']['keys']:
                try:
                    result[name] = self.read(name)
                except:
                    pass

        return result

    def delete(self, name):
        log.info("[DELETE] {}".format(name))

        self.stop_mount(name)

        (rc, _) = self.api(
            "/v1/secret/data/mounts/{}".format(name), 
            method='DELETE'
        )

        if rc != 204:
            raise Exception("status code: {}".format(rc))


    def read(self, name, secrets=False):
        log.info("[READ] {}".format(name))

        (rc, data) = self.api(
            "/v1/secret/data/mounts/{}".format(name), 
            method='GET'
        )

        if rc != 200:
            raise Exception("status code: {}".format(rc))

        data = json.loads(data)['data']['data']

        if not secrets:
            data.pop('secrets', None)

        return data

    def write(self, name, config):
        log.info("[WRITE] {}".format(name))

        try:
            payload = self.read(name, secrets=True)
        except:
            payload = {}

        update = False

        if 'pass' in config:
            # Make sure the password is stored in obfuscated form
            try:
                # If this doesn't throw exception,
                # it is obfuscated already, which is good !
                _ = run(['rclone', 'reveal', config['pass']]),
            except:
                config['pass'] = run(['rclone', 'obscure', config['pass']])

        if 'secrets' not in payload:
            # Initialize secrets for encrypted mountpoint
            payload['secrets'] = {
                'pass': run(['rclone', 'obscure', str(uuid.uuid4())]),
                'path': str(uuid.uuid4())
            }

            update = True
        else:
            # Make sure 'secrets' can never be provided from external input !
            config.pop('secrets', None)

            for k,v in config.items():
                if k not in payload or payload[k] != v:
                    update = True
                    break

        if update:
            payload.update(config)

            (rc, _) = self.api(
                "/v1/secret/data/mounts/{}".format(name), 
                method="POST", 
                payload={ 'data': payload }
            )

            if rc != 200:
                raise Exception("status code: {}".format(rc))

        self.start_mount(name)

    def dump(self):
        return self.mounts()

    def passphrase(self, admin, reset=False):
        if (reset):

            payload={ 'passphrase': str(uuid.uuid4()) }

            (rc, _) = self.api(
                "/v1/secret/data/admin/{}".format(admin), 
                 method="POST", 
                payload={ 'data': payload }
            )
        else:
            (rc, data) = self.api(
                "/v1/secret/data/admin/{}".format(admin), 
                method='GET'
            )
            payload = json.loads(data)['data']['data']

        if rc != 200:
            raise Exception("status code: {}".format(rc))

        return payload

    def get_passphrases(self):
        result = {}

        (rc, data) = self.api(
            "/v1/secret/metadata/admin",
            method="LIST"
        )

        if rc == 200:
            for admin in json.loads(data)['data']['keys']:
                try:
                    result[admin] = self.passphrase(admin, reset=False)['passphrase']
                except:
                    pass

        return result

    def get_config(self, filename):

        config = configparser.ConfigParser()

        for name, details in self.dump().items():
            config[name] = details

        with open(filename, 'w') as f:
            config.write(f)

    def put_config(self, filename):

        config = configparser.ConfigParser()
        config.read(filename)

        for name in config.sections():
            self.write(name, config[name])

    def write_rclone_private_config(self, name):
        try:
            details = self.read(mount, secrets=True)
        except:
            self.stop(mount)
            return
        
        config = configparser.ConfigParser()

        try:
            secrets = details.pop('secrets', None)

            config[name+'_src'] = details

            config[name] = {
                'type': 'crypt',
                'remote': name+'_src:'+secrets['path'], 
                'password': secrets['pass'],
                'filename_encryption': 'off',
                'directory_name_encryption': 'false'
            }
        except Exception as e:
            log.error("Error during config: {}: {}".format(name, str(e)))
            return
    
        with open(settings.USERS_CONFIG_PATH+'/'+name+'.conf', 'w') as f:
            config.write(f)

    def read_rclone_private_config(self, name):

        write_rclone_private_config(name)

        with open(settings.USERS_CONFIG_PATH+'/'+name+'.conf', 'r') as f:
            return read(f)

        raise Exception(f"Config: {name} does not exist")

    def md5_mount_filename(self, name):
        return '/usr/local/etc/'+name+'.md5'

    def web_mount_filename(self, name):
        return '/etc/mounts/'+name+'.conf'

    def pam_mount_filename(self, name):
        return '/etc/mounts/'+name+'.pam'

    def md5_mount_digest(self, name):
        try:
            details = self.read(name)

            md5 = hashlib.md5()
            encoded = json.dumps(details, sort_keys=True).encode()
            md5.update(encoded)
            return md5.hexdigest()
        except:
            return None

    def stop_mount(self, name):

        try:
            log.info("Stopping mount: {}".format(name))

            pid = pipe(
                [
                    ['ps', 'ax'],
                    ['grep', 'rclone'],
                    ['grep', 'webdav/'+name]
                ]
            ).split()[0]

            log.info('Stopping process: {}'.format(pid))
            run(['kill', '{}'.format(pid)])
        except Exception as e:
            log.error("Error stopping mount: {}: {}".format(name, str(e)))

        try:
            os.remove(self.md5_mount_filename(name))
        except Exception as e:
            log.error("Error remove md5 hash: {}: {}".format(name, str(e)))

        try:
            os.remove(self.pam_mount_filename(name))
        except Exception as e:
            log.error("Error remove pam config: {}: {}".format(name, str(e)))

        try:
            os.remove(self.web_mount_filename(name))
            # make sure pending session are rerouted...
            with open(self.web_mount_filename(name), 'w') as f:
                f.write(f"""
                    location /webdav/{name}/ {{  
                        root /usr/share/nginx/html;
                        internal;                    
                    }}
                    """
                )
        except Exception as e:
            log.error("Error remove web config: {}: {}".format(name, str(e)))

        try:
            os.remove(settings.USERS_CONFIG_PATH+'/'+name+'.conf')
        except Exception as e:
            log.error("Error remove config: {}: {}".format(name, str(e)))

        self.flush_config()

    def start_mount(self, name):

        self.write_rclone_private_config(name)

        md5_file = self.md5_mount_filename(name)
        md5_new = self.md5_mount_digest(name)

        if md5_new and os.path.exists(md5_file):
            with open(md5_file, 'r') as f:
                md5_old = f.read()
                if md5_old == md5_new:
                    log.info('Not starting: '+name+', it is same config as running instance')
                    return

        self.stop_mount(name)

        with open(md5_file, 'w') as f:
            f.write(md5_new)

        port = find_free_port()
    
        log.info("Free port to use: {}".format(port))

        try:
            spawn([
                'rclone', 
                '--config='+settings.USERS_CONFIG_PATH+'/'+name+'.conf', 
                'serve', 'webdav', name+':',
                '--addr=0.0.0.0:{}'.format(port),
                '--baseurl=webdav/'+name,
                '--cache-dir', settings.CACHE_DIR+'/'+name,
                '--vfs-cache-mode', 'full'
            ])

            with open(self.web_mount_filename(name), 'w') as f:
                f.write(f"""
                    location /webdav/{name}/ {{  
                        auth_pam "Secure area";
                        auth_pam_service_name "{name}";

                        client_max_body_size 0;
                        
                        proxy_pass http://rclone:{port}/webdav/{name}/;
                    }}
                    """
                )

            with open(self.pam_mount_filename(name), 'w') as f:
                entitled = (settings.PAM_VALIDATE_USERS_ENTITLEMENT or "*").strip()
                if entitled.startswith("lambda"):
                    entitled = f"{eval(entitled)(name)}"
                
                f.write(
                    f"auth required {settings.PAM_VALIDATE_USERS} entitled={entitled}\n"
                    "account required pam_permit.so\n"
                )

        except Exception as e:
            log.error("Error during starting: {}: {}".format(name, str(e)))

        self.flush_config()
    
    def flush_config(self):
        config = configparser.ConfigParser()

        for name, details in self.dump().items():
            config[name] = details

        with open(settings.ADMIN_CONFIG_FILE, 'w') as f:
            config.write(f)

    def stop(self):
        for name in self.mounts().keys():
            self.stop_mount(name)

    def start(self):
        for name in self.mounts().keys():
            self.start_mount(name)

