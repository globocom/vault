from krystism/openstack-keystone

ENV OS_TENANT_NAME admin
ENV OS_USERNAME admin

RUN apt-get update
RUN apt-get install -y telnet curl vim

RUN pip install pip --upgrade

COPY ./helpers/docker/keystone/keystone_setup.sh /home/keystone_setup.sh
