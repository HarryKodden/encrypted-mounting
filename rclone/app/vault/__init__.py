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

vault_default_headers = {
        "X-Vault-Token": settings.VAULT_TOKEN,
        "Content-Type": "application/json"
}

CIPHER = 'CIPHER'
CONF_PATH = '/usr/local/etc'

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

def api(uri, method="GET", payload={}, headers=vault_default_headers):
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
    p = subprocess.Popen(cmd, start_new_session=True)
        
class rClone(object):

    def __init__(self):
        self.start()

    def mounts(self, cipher=False):
        log.info("[MOUNTS]...")

        result = {}

        (rc, data) = api(
            "/v1/secret/metadata/mounts",
            method="LIST"
        )
        
        if rc == 200:
            for name in json.loads(data)['data']['keys']:
                try:
                    result[name] = self.read(name, cipher)
                except:
                    pass

        return result

    def delete(self, name):
        log.info("[DELETE] {}".format(name))

        self.stop_mount(name)

        (rc, _) = api(
            "/v1/secret/data/mounts/{}".format(name), 
            method='DELETE'
        )

        if rc != 204:
            raise Exception("status code: {}".format(rc))


    def read(self, name, cipher=False):
        log.info("[READ] {}".format(name))

        (rc, data) = api(
            "/v1/secret/data/mounts/{}".format(name), 
            method='GET'
        )

        if rc != 200:
            raise Exception("status code: {}".format(rc))

        data = json.loads(data)['data']['data']

        if not cipher:
            data.pop(CIPHER, None)

        return data

    def write(self, name, config):
        log.info("[WRITE] {}".format(name))

        try:
            payload = self.read(name, cipher=True)
        except:
            payload = {}

        if CIPHER not in payload:
            payload[CIPHER] = str(uuid.uuid4())
        
        payload.update(config)

        (rc, _) = api(
            "/v1/secret/data/mounts/{}".format(name), 
            method="POST", 
            payload={ 'data': payload }
        )

        if rc != 200:
            raise Exception("status code: {}".format(rc))

        self.start_mount(name)

    def get_config(self, filename):
        log.info("[GET CONFIG] {}".format(filename))

        config = configparser.ConfigParser()

        dump = self.mounts()

        for name, details in dump.items():
            config[name] = details

        with open(filename, 'w') as f:
            config.write(f)

        return dump

    def put_config(self, filename):
        log.info("[PUT CONFIG] {}".format(filename))

        config = configparser.ConfigParser()
        config.read(filename)

        for name in config.sections():
            self.write(name, config[name])

    def hash_mount_filename(self, name):
        return '/usr/local/etc/'+name+'.md5'

    def hash_mount_digest(self, name):
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

            log.info('Remove hashfile: {}'.format(self.hash_mount_filename(name)))
            run(['rm', '{}'.format(self.hash_mount_filename(name))])

        except Exception as e:
            log.error("Error during stopping: {}: {}".format(name, str(e)))
    
    def start_mount(self, name):

        try:
            details = self.read(name, cipher=True)
        except:
            self.stop(name)
            return
        
        config = configparser.ConfigParser()

        try:
            password = run(['rclone', 'obscure', details.pop(CIPHER, None)])

            config[name+'_src'] = details

            config[name] = {
                'type': 'crypt',
                'remote': name+'_src:encrypted', 
                'password': password,
                'filename_encryption': 'off',
                'directory_name_encryption': 'false'
            }
        except Exception as e:
            log.error("Error during config: {}: {}".format(name, str(e)))
            return
    
        with open(CONF_PATH+'/'+name+'.conf', 'w') as f:
            config.write(f)

        with open(CONF_PATH+'/'+name+'.conf', 'r') as f:
            data = f.read() 
            log.info('\n\n'+data)

        md5_file = self.hash_mount_filename(name)
        md5_new = self.hash_mount_digest(name)

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
                '--config='+CONF_PATH+'/'+name+'.conf', 
                'serve', 'webdav', name+':',
                '--addr=0.0.0.0:{}'.format(port),
                '--baseurl=webdav/'+name,
                '--cache-dir', settings.CACHE_DIR+'/'+name,
                '--vfs-cache-mode', 'full'
            ])

            with open('/etc/mounts/'+name+'.conf', 'w') as f:
                f.write(f"""
                    location /webdav/{name}/ {{  
                        auth_pam "Secure area";
                        auth_pam_service_name "{name}";

                        client_max_body_size 0;
                        
                        proxy_pass http://rclone:{port}/webdav/{name}/;
                    }}
                    """
                )

            with open('/etc/mounts/'+name, 'w') as f:
                f.write(
                    "auth required pam_python.so "
                    "/usr/local/bin/vault-pam-wallet.py "
                    f"url={settings.SRAM_WALLET_URL} "
                    f"service={settings.SRAN_USERS_GROUP}\n"
                    "account required pam_permit.so\n"
                )

        except Exception as e:
            log.error("Error during starting: {}: {}".format(name, str(e)))
    
    def stop(self):
        for name in self.mounts().keys():
            self.stop_mount(name)

    def start(self):
        for name in self.mounts().keys():
            self.start_mount(name)
