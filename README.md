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

### Registering a Storage backend

```plantuml
!include assets/rclone_co_admin.iuml
```

(1) The used encryption key is stored in Vault and used for:
* (re-)generate rclone config
* emergency decryption option of encrypted data

After these steps the generated encryption key is not stored otherwise. The rclone config only holds a hashed value of that encryption key.

(2) The generated rclone config consist of 2 remote definitions:
* The first section specifies how to access the remote storage based on properties given during registration (and testing the connection)
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

### Using a storage backed (Read/Write encrypted only)

```plantuml
!include assets/rclone_co_member.iuml
``` 

(1) This WebDav endpoint will be a HTTPS secured endpoint. The webDav storage available to the user will be the 'encrypted rclone remote backend' exclusively.

User access is granted via Basic Authentication (combination userid/password). The User has to retrieve his personal credentials via the separate flow accessing his personal wallet. (*)
His wallet is only accessible after succesfull SRAM authentication.

Using credentials like userid/password allows mounting the webDav endpoint via standard Mac- and Windows Finders.

(*) Please note: The credentials used by the end-user to authenticate to the webDav is independent of the encryption key used to encrypt/decrypt the data on the storage bac

# Proof Of Concept

During a [POC](./POC.md) excercise the functionality is demonstrated.