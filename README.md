# Encrypted Mounting

The objective of this Proof of Concept is to allow a group of Researcher work together sharing files that can be encrypted automatically.
The collaboration of the team is managed by SRAM. Only active members of SRAM can mount the ecrypted volume.

Functional the mount process will look like this:

```plantuml
!include assets/overall.iuml
```

## Identified solutions

< TO BE COMPLETED, action Tineke >

## rClone + webDav

```plantuml
!include assets/rclone_co_admin.iuml
```

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


```plantuml
!include assets/rclone_co_member.iuml
``` 

(1) This WebDav endpoint will be a HTTPS secured endpoint end access is granted via user specific credentials (combination userid/password). The User has to retrieve his personal credentials via the separate flow accessing his personal wallet.
His wallet is only accessible after succesfull SRAM authentication.

Using credentials like userid/password allows mounting the webDav endpoint via standard Mac- and Windows Finders.