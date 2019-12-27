#!/bin/bash
exec > >(tee -i ~/keystone.log)
exec 2>&1

set -x

# Keystone config
: ${OS_IDENTITY_API_VERSION:=3}
: ${OS_IDENTITY_SERVICE_NAME:=keystone}
: ${OS_IDENTITY_ADMIN_DOMAIN:=default}
: ${OS_IDENTITY_ADMIN_PROJECT:=admin}
: ${OS_IDENTITY_ADMIN_USERNAME:=admin}
: ${OS_IDENTITY_ADMIN_PASSWD:=ADMIN_PASS}
: ${OS_IDENTITY_ADMIN_ROLE:=admin}
: ${OS_IDENTITY_URL_ADMIN:=http://127.0.0.1:35357}
: ${OS_IDENTITY_URL_INTERNAL:=http://127.0.0.1:5000}
: ${OS_IDENTITY_URL_PUBLIC:=http://127.0.0.1:5000}

# Swift config
: ${OS_OBJECTSTORE_SERVICE_REGION:=RegionOne}
: ${OS_OBJECTSTORE_SERVICE_NAME:=swift}
: ${OS_OBJECTSTORE_SERVICE_DESC:=Swift Object Storage}
: ${OS_OBJECTSTORE_DOMAIN:=default}
: ${OS_OBJECTSTORE_PROJECT:=swift}
: ${OS_OBJECTSTORE_USERNAME:=swift}
: ${OS_OBJECTSTORE_PASSWD:=SWIFT_PASS}
: ${OS_OBJECTSTORE_ROLE:=admin}
: ${OS_OBJECTSTORE_URL_ADMIN:=http://vault_swift/v1/AUTH_%(tenant_id)s}
: ${OS_OBJECTSTORE_URL_INTERNAL:=http://vault_swift/v1/AUTH_%(tenant_id)s}
: ${OS_OBJECTSTORE_URL_PUBLIC:=http://vault_swift/v1/AUTH_%(tenant_id)s}

echo 'Keystone Config:'
keystone-manage credential_setup --keystone-user root --keystone-group root
keystone-manage fernet_setup --keystone-user root --keystone-group root
keystone-manage db_sync
keystone-manage bootstrap \
  --bootstrap-project-name "$OS_IDENTITY_ADMIN_PROJECT" \
  --bootstrap-username "$OS_IDENTITY_ADMIN_USERNAME" \
  --bootstrap-username "$OS_IDENTITY_ADMIN_USERNAME" \
  --bootstrap-password "$OS_IDENTITY_ADMIN_PASSWD" \
  --bootstrap-role-name "$OS_IDENTITY_ADMIN_ROLE" \
  --bootstrap-service-name "$OS_IDENTITY_SERVICE_NAME" \
  --bootstrap-region-id "RegionOne" \
  --bootstrap-admin-url "http://vault_keystone:35357/v2.0" \
  --bootstrap-public-url "http://vault_keystone:5000/v2.0" \
  --bootstrap-internal-url "http://vault_keystone:5000/v2.0"

# Start uwsgi
echo 'Start Keystone admin:'
uwsgi --http 0.0.0.0:35357 --wsgi-file $(which keystone-wsgi-admin) &
sleep 5

echo 'Start Keystone public:'
uwsgi --http 0.0.0.0:5000 --wsgi-file $(which keystone-wsgi-admin) &
sleep 5

while ! nc -z 127.0.0.1 35357; do
  sleep 1
done

# Admin credentials
cat >~/keystonerc <<EOF
export OS_AUTH_URL="$OS_IDENTITY_URL_ADMIN"
export OS_IDENTITY_API_VERSION="$OS_IDENTITY_API_VERSION"
export OS_USER_DOMAIN_ID="$OS_IDENTITY_ADMIN_DOMAIN"
export OS_USERNAME="$OS_IDENTITY_ADMIN_USERNAME"
export OS_PASSWORD="$OS_IDENTITY_ADMIN_PASSWD"
export OS_PROJECT_DOMAIN_ID="$OS_IDENTITY_ADMIN_DOMAIN"
export OS_PROJECT_NAME="$OS_IDENTITY_ADMIN_PROJECT"
EOF
source ~/keystonerc

# Object store service
echo 'Register Swift:'
openstack role create 'swiftoperator'
openstack project create "$OS_OBJECTSTORE_PROJECT"
openstack user create --password "$OS_OBJECTSTORE_PASSWD" --project "$OS_OBJECTSTORE_PROJECT" "$OS_OBJECTSTORE_USERNAME"
openstack role add --user "$OS_OBJECTSTORE_USERNAME" --project "$OS_OBJECTSTORE_PROJECT" "$OS_OBJECTSTORE_ROLE"
openstack service create --name "$OS_OBJECTSTORE_SERVICE_NAME" --description "$OS_OBJECTSTORE_SERVICE_DESC" 'object-store'
openstack endpoint create --region "$OS_OBJECTSTORE_SERVICE_REGION" 'object-store' public   "$OS_OBJECTSTORE_URL_PUBLIC"
openstack endpoint create --region "$OS_OBJECTSTORE_SERVICE_REGION" 'object-store' internal "$OS_OBJECTSTORE_URL_INTERNAL"
openstack endpoint create --region "$OS_OBJECTSTORE_SERVICE_REGION" 'object-store' admin    "$OS_OBJECTSTORE_URL_ADMIN"

# Vault user
openstack project create "Vault"
openstack user create --password "u_vault" --project "Vault" "u_vault"
openstack role add --user "u_vault" --project "Vault" "admin"
openstack role add --user "u_vault" --project "Vault" "swiftoperator"

# Restart uwsgi
pkill uwsgi
sleep 5
uwsgi --http 0.0.0.0:5000 --wsgi-file $(which keystone-wsgi-public) &
sleep 5
uwsgi --http 0.0.0.0:35357 --wsgi-file $(which keystone-wsgi-admin)
