
# Encrypted Mounting

The objective of this Proof of Concept is to allow a group of Researcher work together sharing files that can be encrypted automatically.
The collaboration of the team is managed by SRAM. Only active members of SRAM can mount the ecrypted volume.

Functional the mount process will look like this:


![assets/overall.iuml](https://www.plantuml.com/plantuml/proxy?cache=no&src=https://raw.github.com/HarryKodden/encrypted-mounting/main/assets/overall.iuml)

## Identified solutions

< TO BE COMPLETED, action Tineke >

## rClone + webDav

 
actor CO_admin
CO_admin --> portal: Register storage backend in rclone config
portal --> portal: generate encryption key
portal --> Vault: Store encryption key (1)
portal --> portal: create rclone config (2)
portal --> portal: Adjust apache config (3)


(1) The used encryption key is stored in Vault and used for:
* (re-)generate rclone config
* emergency decryption option of encrypted data

(2) The generated rclone config consist of 2 remote definitions:
* The first section specified how to access the remote storage based on properties given during registration (and testing the connection)
* And on top of that an additional remote section that is using the encryption key (1) for an encrypted mountpoint. Only the encrypted mountoint is used in (3)
 
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


 
actor CO_member
CO_member --> portal: Access webDav endpoint
``` 

## Proof of Concept

< TO BE COMPLETED >