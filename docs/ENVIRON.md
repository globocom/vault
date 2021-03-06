# Vault

## Environment Variables

### VAULT_MYSQL_DB

The name of the database that Vault is meant to generate its tables and store its data.

Example value: `vault`


### VAULT_MYSQL_USER

The MySQL user that has full access to the Vault database.

Example value: `mysql_user`


### VAULT_MYSQL_PASSWORD

The password for the MySQL user that has full access to the Vault database.

Example value: `mysql_pass`


### VAULT_MYSQL_HOST

The host where the MySQL service containing the Vault database is running.

Example value: `mysql.endpoint`


### VAULT_MYSQL_PORT

The port where the MySQL service containing the Vault database is running.

Example value: `3306`


### VAULT_KEYSTONE_USERNAME

The username of the Keystone user that has the *admin* and *ResellerAdmin* roles. This is the user that Vault will use to manage users and projects in Keystone.

Example value: `keystone_user`


### VAULT_KEYSTONE_PASSWORD

The password of the Keystone user that has the *admin* and *ResellerAdmin* roles. This is the user that Vault will use to manage users and projects in Keystone.

Example value: `keystone_password`


### VAULT_KEYSTONE_PROJECT

The Keystone project on which the Keystone user has the *admin* and *ResellerAdmin* roles.

Example value: `Vault`


### VAULT_KEYSTONE_URL

The URL of your Identity API, including port and version.

Example value: `http://keystone.endpoint:5000/v3`


### VAULT_SECRET_KEY

A secret key for this particular Django installation. This is used to provide cryptographic signing, and should be set to a unique, unpredictable value. For more information, see [Django's documentation on the SECRET_KEY setting](https://docs.djangoproject.com/en/3.0/ref/settings/#std:setting-SECRET_KEY).


### IDENTITY_SECRET_KEY

A secret key used for encrypting and decrypting Keystone passwords. This must be generated using the following command:
``` bash
$ python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key())"
```
For more information, see [Cryptography's documentation on Fernet (symmetric encryption)](https://cryptography.io/en/latest/fernet/).


### MAX_FILES_UPLOAD

*(Optional)* The maximum number of files that can be uploaded at once to Swift via the [Bulk Operations middleware](https://www.swiftstack.com/docs/admin/middleware/bulk.html).

Default value: `10`


### VAULT_LANGUAGE

*(Optional)* The language used by Vault. Must be one of the languages in vault/settings.py's `LANGUAGES` list.

Default value: `en-us`


### VAULT_PAGINATION_SIZE

*(Optional)* The number of items displayed per page when listing something in Vault, such as Swift objects or Keystone users.

Default value: `50`


### VAULT_SWIFT_INSECURE

*(Optional)* Set to `True` if using invalid SSL certificates.

Default value: `False`


### VAULT_SWIFT_VERSION_PREFIX

*(Optional)* When versioning is enabled on a Swift container, a new, hidden container is created with its name and this prefix.

Default value: `_version_`
