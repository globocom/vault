#!/bin/bash

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
  --bootstrap-admin-url "http://vault_keystone:35357/v2.0" \
  --bootstrap-public-url "http://vault_keystone:5000/v2.0" \
  --bootstrap-internal-url "http://vault_keystone:5000/v2.0"

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

# Object store service
echo "Register Swift:"
openstack role create "swiftoperator"
openstack project create "swift"
openstack user create --password "SWIFT_PASS" --project "swift" "u_swift"
openstack role add --user "u_swift" --project "swift" "admin"
openstack service create --name "swift" --description "Swift Object Storage" "object-store"
openstack endpoint create --region "RegionOne" "object-store" public "http://vault_swift:8080/v1/AUTH_%(tenant_id)s"
openstack endpoint create --region "RegionOne" "object-store" internal "http://vault_swift:8080/v1/AUTH_%(tenant_id)s"
openstack endpoint create --region "RegionOne" "object-store" admin "http://vault_swift:8080/v1/AUTH_%(tenant_id)s"

# Vault user
openstack project create "Vault" & sleep 2
openstack user create --password "u_vault" --project "Vault" "u_vault" & sleep 2
openstack role add --user "u_vault" --project "Vault" "admin"
openstack role add --user "u_vault" --project "Vault" "swiftoperator"

# Restart uwsgi
pkill uwsgi
sleep 5
uwsgi --http 0.0.0.0:5000 --wsgi-file $(which keystone-wsgi-public) &
sleep 5
uwsgi --http 0.0.0.0:35357 --wsgi-file $(which keystone-wsgi-admin)
