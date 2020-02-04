# Vault
Admin webapp for OpenStack Keystone and OpenStack Swift.

### Short description
Manage users and tenants on your Keystone service.

Manage containers and objects on Swift. (A customized version of [django-swiftbrowser](https://github.com/cschwede/django-swiftbrowser))

## Running with Docker Compose
```
$ make docker-start
```

After a while, Vault will be accessible at localhost:8000. The initial admin user's credentials are:

- *username*: admin
- *password*: admin

For more information on the docker implementation see [DOCKER.md](DOCKER.md).

## Basic setup

This section shows how to setup Vault in your own infrastructure, to facilitate administration of your existing Keystone and Swift services.

### 1. Install dependencies
```
$ pip install -r requirements.txt
```

### 2. Set environment variables
```
$ export VAULT_MYSQL_DB=vault
$ export VAULT_MYSQL_USER=mysql_user
$ export VAULT_MYSQL_PASSWORD=mysql_pass
$ export VAULT_MYSQL_HOST=mysql.endpoint
$ export VAULT_MYSQL_PORT=3306
$ export VAULT_KEYSTONE_USERNAME=keystone_user
$ export VAULT_KEYSTONE_PASSWORD=keystone_password
$ export VAULT_KEYSTONE_PROJECT=Vault
$ export VAULT_KEYSTONE_API_VERSION=2
$ export VAULT_KEYSTONE_URL=http://keystone.endpoint:5000/v2.0
$ export VAULT_KEYSTONE_ROLE=swiftoperator
```

For optional variables and more information on each of the environment variables, see [ENVIRON.md](ENVIRON.md).

### 3. Create a MySQL database and the MySQL user
```
mysql> create database vault;
mysql> CREATE USER 'mysql_user'@'localhost' IDENTIFIED BY 'mysql_pass';
mysql> GRANT ALL PRIVILEGES ON vault.* TO 'mysql_user'@'localhost';

$ python manage.py migrate
```

### 4. Create a superuser
```
$ python manage.py create_user -s
```

You will be asked for a username, e-mail, team and password. A superuser with the provided information will be created. If the team does not yet exist, it will be created. The superuser will be added to the provided team.

Optionally, you can pass the `--username`, `==email` `--teamname` and `--password` arguments, skipping the need to interactively fill out these pieces of information.

The `-s` (or `--superuser`) option makes the new user a superuser, meaning it has admin privileges. For a normal user, don't use this option

### 5. Run
```
$ python manage.py runserver
```

In a production environment, it is recommended to use a WSGI HTTP server. Here's an example using Gunicorn:
```
web: gunicorn --timeout 60 -b 0.0.0.0:$PORT vault.wsgi
```

### Static files
```
$ python manage.py collectstatic --noinput

# Upload your static files to your static_url.

# To upload static files to your current swift cluster, do:

$ cd statictemp
$ swift upload --os-username=<swift-user> --os-password=<swift-pass> --os-tenant-name=<swift-tenant> --os-auth-url=<swift-auth-url> --os-storage-url=<swift-admin-url> <swift-container> vault_static/
```

## Running tests
```
pip install -r requirements_test.txt
make tests
```

## Dependencies

- Django
- Swift
- Keystone

## Locale

How to edit locale files:

```
# In the app directory
django-admin makemessages --all
django-admin compilemessages --locale=pt_BR
```
