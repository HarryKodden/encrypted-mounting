# Encrypted Mounting

The objective of this Proof of Concept is to allow a group of Researcher work together sharing files that can be encrypted automatically.
The collaboration of the team is managed by SRAM. Only active members of SRAM can mount the ecrypted volume.

Functional the mount process will look like this:

```plantuml
actor Researcher as user
database data as data
participant SRAM as sram
participant IDP as idp
user --> data: Mount volume
data --> sram: Enforce authentication
idp --> user: Authenticate !
user --> idp: Logon
idp --> sram: OK
sram --> user: Volume mounted !
```