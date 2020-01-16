#!/bin/bash

create_user() {
    user=$1
    pass=$2
    project=$3
    while : ; do
        user_match=$(openstack user list -f value | grep $user)
        if [[ ! -z "$user_match" ]]; then
            echo "User created"
            break
        else
            echo "Creating user $user"
            openstack user create $user --domain default --password $pass --project $project
            sleep 1
        fi
    done
}

create_project() {
    project=$1
    while : ; do
        project_match=$(openstack project list -f value | grep $project)
        if [[ ! -z "$project_match" ]]; then
            echo "Project created"
            break
        else
            echo "Creating project $project"
            openstack project create $project --domain default --description "Project $project"
            sleep 1
        fi
    done
}

create_role() {
    role=$1
    while : ; do
        role_match=$(openstack role list -f value | grep $role)
        if [[ ! -z "$role_match" ]]; then
            echo "Role created"
            break
        else
            echo "Creating role $role"
            openstack role create $role
            sleep 1
        fi
    done
}

create_role_assign() {
    user=$1
    project=$2
    role=$3
    while : ; do
        assign_match=$(openstack role assignment list -f value --user $user --names | grep $role)
        if [[ ! -z "$assign_match" ]]; then
            echo "Role associated"
            break
        else
            echo "Assign role $role with user $user"
            openstack role add $role --project $project --user $user
            sleep 1
        fi
    done
}

create_service() {
    service=$1
    service_type=$2
    while : ; do
        service_match=$(openstack service list -f value | grep $service)
        if [[ ! -z "$service_match" ]]; then
            echo "Service created"
            break
        else
            echo "Creating service $service"
            openstack service create $service_type --name $service --description "Service $service"
            sleep 1
        fi
    done
}

create_endpoint() {
    service_type=$1
    interface=$2
    endpoint=$3
    while : ; do
        endpoint_match=$(openstack endpoint list -f value --service $service_type --interface $interface | grep $service_type)
        if [[ ! -z "$endpoint_match" ]]; then
            echo "Endpoint created"
            break
        else
            echo "Creating endpoint $interface with url $endpoint"
            openstack endpoint create --region "RegionOne" $service_type $interface $endpoint
            sleep 1
        fi
    done
}
