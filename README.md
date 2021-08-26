<p align="center">
    <img src="https://raw.githubusercontent.com/globocom/vault/master/vault/static/vault/img/screenshot.png" alt="Vault Screenshot" />
</p>

# Vault

[![build status](https://api.travis-ci.org/globocom/vault.svg?branch=master)](http://travis-ci.org/globocom/vault)

Admin webapp for OpenStack Keystone and OpenStack Swift.

### Short description

Manage users and projects on your Keystone service.

Manage containers and objects on Swift. (A customized version of [django-swiftbrowser](https://github.com/cschwede/django-swiftbrowser))

## How Vault works

### Teams

Vault has users and teams. Users have the permission to add other users to their teams. This gives them more autonomy.

### Keystone Projects

Users can create projects that will belong to their teams. A Keystone project corresponds to a Swift account.

### Swift Accounts

Users can create, modify or delete any container or object from accounts owned by one of their teams.

### Administration

An admin can create users and teams, as well as add and remove users from those teams. Admins can also manage Keystone projects and users.

## Running locally with Docker Compose

This section describes how to use Docker Compose to locally setup Vault, running all the necessary services in containers.

```bash
$ make docker-start
```

After a while, Vault will be accessible at localhost:8000. The initial admin user's credentials are:

-   _username_: admin
-   _password_: admin

There will also be a non-admin user available. That user's credentials are:

-   _username_: user
-   _password_: user

For more information on the docker implementation see [Docker](https://github.com/globocom/vault/blob/master/docs/DOCKER.md).

## Basic setup for production environment

This section describes how to setup Vault in your own infrastructure, to facilitate administration of your existing Keystone and Swift services. In this case, Vault will run in your own environment, such as in a Virtual Machine.

### 1. Install dependencies

```bash
$ pip install -r requirements.txt
```

### 2. Set environment variables

```bash
$ export VAULT_MYSQL_DB=vault
$ export VAULT_MYSQL_USER=mysql_user
$ export VAULT_MYSQL_PASSWORD=mysql_pass
$ export VAULT_MYSQL_HOST=mysql.endpoint
$ export VAULT_MYSQL_PORT=3306
$ export VAULT_KEYSTONE_USERNAME=keystone_user
$ export VAULT_KEYSTONE_PASSWORD=keystone_password
$ export VAULT_KEYSTONE_PROJECT=Vault
$ export VAULT_KEYSTONE_URL=http://keystone.endpoint:5000/v3
```

For optional variables and more information on each of the environment variables, see [Environment Variables](https://github.com/globocom/vault/blob/master/docs/ENVIRON.md).

### 3. Create a MySQL database and the MySQL user

```SQL
mysql> create database vault;
mysql> CREATE USER 'mysql_user'@'localhost' IDENTIFIED BY 'mysql_pass';
mysql> GRANT ALL PRIVILEGES ON vault.* TO 'mysql_user'@'localhost';
```

Then

```bash
$ python manage.py migrate
```

### 4. Create a superuser

```bash
$ python manage.py create_user -s
```

You will be asked for a username, e-mail, team and password. A superuser with the provided information will be created. If the team does not yet exist, it will be created. The superuser will be added to the provided team.

Optionally, you can pass the `--username`, `--email`, `--teamname` and `--password` arguments, skipping the need to interactively fill out these pieces of information.

The `-s` (or `--superuser`) option makes the new user a superuser, meaning it has admin privileges. For a normal user, don't use this option.

### 5. Run

```bash
$ python manage.py runserver
```

In a production environment, it is recommended to use a WSGI HTTP server. Here's an example using [Gunicorn](https://gunicorn.org/):

```bash
gunicorn --timeout 60 -b 0.0.0.0:$PORT vault.wsgi
```

## Authentication

Vault uses the default Django authentication, but also allows for OAuth2 authentication via [django-all-access](https://django-all-access.readthedocs.io/en/latest/). To add an OAuth2 provider, simply use the Django admin. For more information, see [OAuth2 Authentication](https://github.com/globocom/vault/blob/master/docs/OAUTH2.md).

Only admins can create new users, unless when using OAuth2 authentication.

## Static files

If you want to upload Vault's static files to your current Swift cluster, simply create a project (named here as `<swift-project>`) and, in that project, a container (named here as `<swift-container>`). Then, using the credentials of a user with permission to write to that container, do the following:

```bash
$ python manage.py collectstatic --noinput
$ swift upload --os-username=<swift-user> --os-password=<swift-pass> --os-project-name=<swift-project> --os-auth-url=<swift-auth-url> --os-storage-url=<swift-admin-url> <swift-container> vault_static/
```

## Running tests

```bash
pip install -r requirements_test.txt
make tests
```

## Creating new apps for Vault

While Vault already delivers an app for Swift management and another for Keystone management, it also allows you to easily implement your own apps. This helps you centralize several services in a single, standardized web interface. For more information, see [How to create a Vault App](https://github.com/globocom/vault/blob/master/docs/APPS.md).

## Dependencies

-   Django
-   Swift
-   Keystone

## Locale

How to edit locale files:

```bash
# In the app directory
django-admin makemessages --all
django-admin compilemessages --locale=pt_BR
```
