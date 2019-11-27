# Vault
Admin webapp for Openstack Keystone and Swift.

### Short description
Manage users and tenants on your Keystone service.

Manage containers and objects on Swift. (A customized version of [django-swiftbrowser](https://github.com/cschwede/django-swiftbrowser))

## Basic setup

1) install dependencies
```
$ pip install -r requirements.txt
```

2) set environment variables
```
$ export VAULT_ENVIRON=PROD
$ export VAULT_MYSQL_USER=<user>
$ export VAULT_MYSQL_PASSWORD=<password>
$ export VAULT_MYSQL_PORT=3306
$ export VAULT_MYSQL_HOST=<host>
$ export VAULT_STATIC_URL='http://static-url'
$ export VAULT_KEYSTONE_URL='https://keystone-url'
```

3) create a mysql database called "vault"
```
mysql> create database vault;

$ python manage.py syncdb
```

4) run
```
$ python manage.py runserver
```

### Static files
```
$ python manage.py collectstatic --noinput

# Upload your static files to your static_url.

# To upload static files to your current swift cluster, do:

$ cd statictemp
$ swift -A https://your-keystone/v3 -V 3 -U <user> -K <password> --os-tenant-name <project> --os-endpoint-type adminURL upload <your-container>
```

### Running tests
```
pip install -r requirements_test.txt
make tests
```

### Running local
```
# Create a virtualenv (using pyenv)
pyenv virtualenv 2.7.11 vault

# Export variables based on vault-dev Tsuru app
for var in $(tsuru app-run env -a vault-dev | grep -E "MYSQL|VAULT_KEYSTONE"); do export $var; done;

# Creates a dump of the database
mysqldump --user $VAULT_MYSQL_USER -p $VAULT_MYSQL_PASSWORD --host $VAULT_MYSQL_HOST $VAULT_MYSQL_DB > /tmp/vault.sql

# Clear the database environment variables
unset VAULT_MYSQL_DB
unset VAULT_MYSQL_HOST
unset VAULT_MYSQL_PASSWORD
unset VAULT_MYSQL_USER

# Restore the database dump on your local database
mysql -u root vault < /tmp/vault.sql

# Run Vault
make run
```

### Dependencies

- Django
- Swift
- Keystone

### Locale

How to edit locale files:

```
# In the app directory
django-admin makemessages --all
django-admin compilemessages --locale=pt_BR
```
