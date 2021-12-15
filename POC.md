# Proof of Concept

In his Proof of Concept the objective is to demonstrate a full integration of rClone, WebDAV, Federated authentication, Encrypted data stored on the backend storage server.

## Config - Sample content...

For setting up the demonstration environment, we need some kind of configuration. In the future this configuration could be the result of an administrative web function in which the administrator can enter these variables. The resulting configuration could be stored for example as a secret on the Vault Server.

For now, this config is just a JSON dictionary. A Python script reads this configuration and generates all the necessary configuration components.

```config
config = [
        {
        'name': 'sample',
        'rclone_config' : {
            'type': 'webdav'
            'url': 'https://researchdrive.surfsara.nl/remote.php/nonshib-webdav'
            'vendor': 'other'
            'user': 'harry.kodden@surf.nl'
            'pass': '...undisclosed...'
        },
        'encryption_secret': 'ynsnEvyqnawgD2TAXn6^tkuuPhwQQNnzukUE{Pf',
        'authorized_sram_groups': ['surfresearch.sram_demo.testje'],
        'network': 'localnet'
    }
]
```

Based on this config, several config files are generated.

| type | meaning | example |
| -- | -- | --|
| rclone | The config that rClone requires to setup the mountpoints | [**sample\\rclone.conf**](#generated-samplercloneconf) |
| docker | A docker compose file is generated to start the rclone container servicing a webDaV endpoint to the encrypted storage location | [**sample\\docker.conf**](#generated-sampledockerconf)   |
| apache | A location section is generated, that will forward requests on the public HTTP endpoint towards the rClone container on the private shielded network | [**sample\\apache.conf**](#generated-sampleapacheconf) |
| pam | This PAM file will handle authentication requests. The authentication will be validated by matching the given password against a Vault stored secret of the user. In order to retrieve hist secret, the user first has to open his Vault Wallet and that requires SRAM aurthentication first.| [**sample\\pam.conf**](#generated-samplepamconf) |
| bash | This script will fire up the service, starting the rclone docker container, adding the PAM script oto the system PAM stack, adding the location to the Apache config and restarting Apache to activate the endpoint | [**sample\\start.sh**](#generated-samplestartsh) |
| bash | This script will close down the service, removing the HTTP endpoint to the container, removing the PAM section, and terminate the rclone container | [**sample\\stop.sh**](#generated-samplestopsh) |

From all components the examples are given based on the given config.

**Global constants are:**
* Public domain address, a FQDN of the webserver on which the webdav mountpoint will be made available. The FQDN used in below examples is **https://demo.example.org**
* FQDN address for the Validation endpoint at which the user given password will be validated with the authorization server, in below example this is **https://vault.example.org**

Here are the generated configuration components

# Generated: sample\\rclone.conf

```config
# Do Not Edit: Generated File

[storage]
type = webdav
url = https://researchdrive.surfsara.nl/remote.php/nonshib-webdav
vendor = other
user = harry.kodden@surf.nl
pass = ...undisclosed...

[encrypted]
type = crypt
remote = storage:
password = ...undisclosed: <encryption_secret>...
```

# Generated: sample\\docker.conf

```config
# Do Not Edit: Generated File
version: '3'

services:

  rclone-webdav-sample:
    container_name: sample
    image: rclone/rclone
    volumes:
      - ./rclone.conf:/etc/rclone.conf
    command:
      - "--config"
      - "/etc/rclone.conf"
      - "--verbose"
      - "serve"
      - "webdav"
      - "encrypted:"
      - "--addr"
      - "0.0.0.0:8080"
      - "--vfs-cache-mode"
      - "full"
    restart: unless-stopped
    networks:
      - internal

networks:
  internal:
    external:
      name: localnet
```

# Generated: sample\\pam.conf

```config
# Do Not Edit: Generated File

auth sufficient pam_python.so /usr/local/bin/vault-pam-wallet.py url=https://vault.example.org service=surfresearch.sram_demo.testje
account required pam_permit.so
```


# Generated: sample\apache.conf

```config
# Do Not Edit: Generated File

<LocationMatch "^/webdav/sample/(.*)$">
    AuthType Basic
    AuthName "private area"
    AuthBasicProvider PAM
    AuthPAMService sample
    require valid-user

    ProxyPass http://sample:8080/$1
    ProxyPassReverse http://sample:8080/$1
</LocationMatch>
```

# Generated: sample\start.sh

```config
# Do Not Edit: Generated File

# startup rclone container...
docker-compose -f docker.conf up -d

# install the PAM config
docker cp pam.conf portal:/etc/pam.d/sample

# install the Apache location endpoint
docker cp apache.conf portal:/etc/apache2/webdav/sample.conf

# reload apache to activation changes...
docker exec portal apachectl -k graceful
```

# Generated: sample\stop.sh

```config
# Do Not Edit: Generated File

# remove PAM config --> users can no longer mount !
docker exec portal rm /etc/pam.d/sample

# remove Apache location
docker exec portal rm /etc/apache2/webdav/sample.conf

# reload apache to activate changes...
docker exec portal apachectl -k graceful

# stop rclone container !
docker-compose -f docker.conf down -v
```

# Result

Users can mount to **https://demo.example.org/webdav/sample** and authenticate using their SRAM username and a password that matches his personal secret for this group **surfresearch.sram_demo.testje**.
The user can retrieve this secret by visiting his wallet at **https://vault.example.org/wallet**