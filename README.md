# Encrypted Mounting

The objective of this Proof of Concept is to allow a group of Researcher work together sharing files that can be encrypted automatically.
The collaboration of the team is managed by SRAM. Only active members of SRAM can mount the ecrypted volume.

Functional the mount process will look like this:

```plantuml
!include assets/overall.iuml
```

## Identified solutions

- Safely collaborate and store privacy sensitive documents on research cloud.
- Create a safe portal for applications to submit sensitive data that can only be investigated by active members.
- Manage user access by not connecting the encrypted folder to a specific person.

## rClone + webDav

### Registering a Storage backend

```plantuml
!include assets/rclone_co_admin.iuml
```

(1) The used encryption key is stored in Vault and used for:

- (re-)generate rclone config
- emergency decryption option of encrypted data

After these steps the generated encryption key is not stored otherwise. The rclone config only holds a hashed value of that encryption key.

(2) The generated rclone config consist of 2 remote definitions:

- The first section specifies how to access the remote storage based on properties given during registration (and testing the connection)
- And on top of that an additional remote section that is using the encryption key (1) for an encrypted mountpoint. Only the encrypted mountoint is used in (3)

example:

```rclone
[mydata]
type = sftp
host = example.stackstorage.com
user = user@example.com
port = 22
pass = <...>
key_file_pass = <...>

[encrypted]
type = crypt
remote = remote:mydata
password = < hash of encryption key >
```

(3) The Apache config added to the portal offers a webDav url to access the rclone encrypted remote backend

### Using a storage backed (Read/Write encrypted only)

```plantuml
!include assets/rclone_co_member.iuml
```

(1) This WebDav endpoint will be a HTTPS secured endpoint. The webDav storage available to the user will be the 'encrypted rclone remote backend' exclusively.

User access is granted via Basic Authentication (combination userid/password). The User has to retrieve his personal credentials via the separate flow accessing his personal wallet. (\*)
His wallet is only accessible after succesfull SRAM authentication.

Using credentials like userid/password allows mounting the webDav endpoint via standard Mac- and Windows Finders.

(\*) Please note: The credentials used by the end-user to authenticate to the webDav is independent of the encryption key used to encrypt/decrypt the data on the storage bac

# Proof Of Concept

During a [POC](./POC.md) excercise the functionality is demonstrated.

# Setting up encrypted mounting on a Research Cloud VM.

## Setting up your domain

make sure you have your own domain name pointed at the ip-address of your machine and also a wildcard DNS record for that domain. So register a fixed ip-address first in research cloud and then register the domain to resolve to that ip-address:

```bash
your-domain.com    --> IP-address
*.your-domain.com   --> IP-address
```

You need to set the registered domain name and ansible_user in `./ansible/inventory/workspace`, For easy use, register your Research Cloud user name at ansible_user. This user is used for deployment and allready had the appropriate ssh keys.

```shell
[workspace]
your-domain.com

[workspace:vars]
ansible_python_interpreter=/usr/bin/python3
ansible_user=rinsrutgers
```

## Settting the environment variables

Move the example environment file to the appropriate place and rename:

```shell
mv ./ansible/.env.sample ./ansible/.env
```

Fill in the following configuration:

```
# SRAM URL.
SRAM_URL=https://sram.surf.nl

# OIDC connection with SRAM for Administrator authentication
SRAM_OIDC_BASE_URL=https://proxy.sram.surf.nl
SRAM_OIDC_CLIENT_ID=< SRAM Registered client id >
SRAM_OIDC_CLIENT_SECRET=< Secret key>

# OIDC Authenticated users will need a claim "eduperson_entitlement" that contains the value of the SRAM_ADMIN_ACCESS_GROUP
# in order to be authorized to control the admin dashboard.
SRAM_ADMIN_ACCESS_GROUP=urn:mace:surf.nl:sram:group <specify as the group as detailed as you wish...>

# This is the Service API key that is used to validate authorized users of this service.
# SRAM users need to be part of a SRAM Collaboration connected to this service
# AND the users has to have created to SRAM Token for that same service.
SRAM_SERVICE_BEARER_TOKEN=< token from SRAM collaboration, generate token within sram.>

# This will be the administrator password to access the Traefik dashboard, eg "https://proxy.<domain>/dashboard/
PROXY_ADMIN_PASSWORD=< Put your secret here !>
```

## Deployment

Deploy encrypted mounting on Research Cloud from your own machine, make sure you are in the `./ansible` directory:

```shell
cd ansible
export $(cat .env | xargs)
ansible-playbook -i inventory/workspace playbook.yml
```

To deploy on AWS you can use the Terraform scripts.

```shell
cd terraform
export $(cat .env | xargs)
terraform init
terraform plan
terraform apply
```

## After deployment the following endpoints are available:

> ## vault.your-domain.com
>
> - Choose Token as login method
> - Get your password from the Research Cloud VM from: `/opt/vault/etc/rootkey`
>
> This brings you to the vault which is storing all sensitive encryption keys

> ## proxy.your-domain.com/dashboard
>
> - Your username is admin
> - Your password is the one you choose during step X
>
> This interface brings you to the proxy portal where you can inspect how all traffic is routed.

> ## mount.your-domain.com/admin
>
> - Your username is your SRAM username, you can find it in your profile.
> - Your login will be handled bij SRAM itself.
>
> This interface brings you to the Rclone admin panel. From here you will set up your encrypted folders by attaching external cloud storage. Rclone supports over 40 cloud storage providers, so you are not limited to Research Cloud but you could also mount google drive or onedrive.
> Every `encrypted mount` is configured by a config file, this is either created by a step by step interactive way (on this endpoint) or plain text (the next endpoint). The name of this configuration block will also be used on the webdav mount later on.

> ## mount.your-domain.com/admin/api/doc
>
> This endpoint brings you to a swagger documentation page where you can test out the API of the systen. This is particculary useful to quickly download or test your configuration files.
>
> - Authentication is handled in the same way as the admin panel.

> ## mount.your-domain.com/webdav/your-rclone-config-name
>
> - Your username is your SRAM username, you can find it in your profile.
> - Your password is a token from SRAM. To get it, log in to SRAM and go to _Tokens_ and generate one, copy it and carefully store it in a password manager, you will not be able to see it again.
>
> This endpoint is used to access your encrypted mounting point trough the webDav protocol, by doing so it is accessible via standard Mac- and Windows Finders with a userid/password.
