#!/bin/bash
python manage.py collectstatic --noinput && \
cd /home/application/current && \
simpleswift --os-auth-url $SWIFT_AUTH_URL \
            --os-username $SWIFT_USER \
            --os-password $SWIFT_PASSWORD \
            --os-tenant-name $SWIFT_TENANT \
            upload $SWIFT_CONTAINER vault_static/
