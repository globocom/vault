#!/bin/bash

while : ; do
    project=$(docker ps | grep vault_keystone)
    if [[ ! -z "$project" ]]; then
        break;
    else
        sleep 1;
    fi
done

docker exec vault_keystone "/home/keystone_setup.sh"
