#!/bin/bash

source /etc/bootstrap_fn.sh

exec > >(tee -i /etc/keystone/keystone.log)
exec 2>&1

set -x

# Keystone config
echo "Keystone Config:"
keystone-manage credential_setup --keystone-user root --keystone-group root
keystone-manage fernet_setup --keystone-user root --keystone-group root
keystone-manage db_sync
keystone-manage bootstrap \
  --bootstrap-project-name "admin" \
  --bootstrap-username "admin" \
  --bootstrap-password "ADMIN_PASS" \
  --bootstrap-role-name "admin" \
  --bootstrap-service-name "keystone" \
  --bootstrap-region-id "RegionOne" \
  --bootstrap-admin-url "http://localhost:35357/v2.0" \
  --bootstrap-public-url "http://localhost:5000/v2.0" \
  --bootstrap-internal-url "http://localhost:5000/v2.0"

# Start uwsgi
echo "Start Keystone admin:"
uwsgi --http 0.0.0.0:35357 --wsgi-file $(which keystone-wsgi-admin) &
sleep 5

echo "Start Keystone public:"
uwsgi --http 0.0.0.0:5000 --wsgi-file $(which keystone-wsgi-admin) &
sleep 5

while ! nc -z 127.0.0.1 35357; do
  sleep 1
done

# Admin credentials
cat >/etc/keystone/keystonerc <<EOF
export OS_AUTH_URL="http://127.0.0.1:35357"
export OS_IDENTITY_API_VERSION="3"
export OS_USER_DOMAIN_ID="default"
export OS_PROJECT_DOMAIN_ID="default"
export OS_PROJECT_NAME="admin"
export OS_USERNAME="admin"
export OS_PASSWORD="ADMIN_PASS"
EOF
source /etc/keystone/keystonerc

# Swift object store service
create_project swift
create_user u_swift SWIFT_PASS swift
create_role swiftoperator
create_role ResellerAdmin
create_role_assign u_swift swift admin
create_role_assign u_swift swift ResellerAdmin
create_service swift "object-store"
create_endpoint "object-store" public "http://localhost:8080/v1/AUTH_%(tenant_id)s"
create_endpoint "object-store" internal "http://localhost:8080/v1/AUTH_%(tenant_id)s"
create_endpoint "object-store" admin "http://localhost:8080/v1/AUTH_%(tenant_id)s"

# Vault project and user
create_project Vault
create_user u_vault u_vault Vault
create_role_assign u_vault Vault admin
create_role_assign u_vault Vault swiftoperator
create_role_assign u_vault Vault ResellerAdmin

# Restart uwsgi
pkill uwsgi
sleep 5
uwsgi --http 0.0.0.0:5000 --wsgi-file $(which keystone-wsgi-public) &
sleep 5
uwsgi --http 0.0.0.0:35357 --wsgi-file $(which keystone-wsgi-admin)
