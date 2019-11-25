# Vault
Admin webapp for Openstack's Keystone and Swift..


### Short description
Manage users and tenants on your Keystone service.

Manage containers and objects on Swift. (A customized version of [django-swiftbrowser](https://github.com/cschwede/django-swiftbrowser))

### Basic setup (production)
=======

1) install dependencies

    $ pip install -r requirements.txt.

2) set environment variables

    $ export VAULT_ENVIRON=PROD
    $ export VAULT_MYSQL_USER=(vault mysql user)
    $ export VAULT_MYSQL_PASSWORD=(vault mysql password)
    $ export VAULT_MYSQL_PORT=3306
    $ export VAULT_MYSQL_HOST=(vault mysql host)
    $ export VAULT_STATIC_URL='http://your-static-url'
    $ export VAULT_KEYSTONE_URL='https://your-keystone-url:5000'

3) create a mysql database "vault"

    # on mysql: 'create database vault;'
    $ python manage.py syncdb

4) run

    $ python manage.py runserver

### static files
    $ python manage.py collectstatic --noinput

    # upload your static files to your static_url
    # if Swift do:
    $ cd statictemp
    $ swift -A https://your-keystone-url:5000/v2.0 -V 2.0 -U <user> -K <password> --os-tenant-name <project> --os-endpoint-type adminURL upload <your-container> .

### To run tests
    pip install -r requirements_test.txt
    make tests

### To run local (based on dev environment)
```
# Create a virtualenv (using pyenv)
pyenv virtualenv 2.7.11 vault

# Export variables based on vault-dev Tsuru app
for var in $(tsuru app-run env -a vault-dev | grep -E "MYSQL|VAULT_KEYSTONE"); do export $var; done;

# Creates a dump of the database
mysqldump --user $VAULT_MYSQL_USER -p$VAULT_MYSQL_PASSWORD --host $VAULT_MYSQL_HOST $VAULT_MYSQL_DB > /tmp/vault.sql

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

=======
### Compatibilities

- Django 1.11
- Swift 2.1.0 (auth v2.0)
- Keystone 2014.1

### Locale

How to edit locale files:

```
brew install gettext
brew link gettext --force

# In the app directory
django-admin makemessages --all
django-admin compilemessages --locale=pt_BR
```
