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

### VAULT_KEYSTONE_API_VERSION

The version of the Identity API used on your Keystone service. Can be either `2` or `3`.

Example value: `2`

### VAULT_KEYSTONE_URL

The URL of your Identity API, including port and version.

Example value: `http://keystone.endpoint:5000/v2.0`


### VAULT_KEYSTONE_ROLE

The role registered in your Keystone service that is needed to operate Swift.

Example value: `swiftoperator`
