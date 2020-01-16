FROM ubuntu:18.04

RUN DEBIAN_FRONTEND=noninteractive apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get upgrade -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        attr \
        liberasurecode1 \
        memcached \
        python-dnspython \
        python-eventlet \
        python-greenlet \
        python-lxml \
        python-netifaces \
        python-pastedeploy \
        python-pip \
        python-pyeclib \
        python-setuptools \
        python-simplejson \
        python-xattr \
        rsyslog \
        rsync \
        sqlite3 \
        sudo \
        xfsprogs && \
    DEBIAN_FRONTEND=noninteractive apt-get clean && \
    rm -rf /var/lib/apt/lists/* && \
    pip install --upgrade pip setuptools pytz

RUN DEBIAN_FRONTEND=noninteractive apt-get update && \
    apt-get install -y --no-install-recommends git-core && \
    git clone --branch 3.8.1 --single-branch --depth 1 https://github.com/openstack/python-swiftclient.git /usr/local/src/python-swiftclient && \
    cd /usr/local/src/python-swiftclient && python setup.py develop && \
    git clone --branch 2.23.0 --single-branch --depth 1 https://github.com/openstack/swift.git /usr/local/src/swift && \
    cd /usr/local/src/swift && python setup.py develop && \
    apt-get remove -y --purge git-core git && \
    apt-get autoremove -y --purge && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Pike
RUN pip install keystoneauth1==3.4.1 keystonemiddleware==4.22.0

COPY ./helpers/docker/swift/swift /etc/swift
COPY ./helpers/docker/swift/misc/rsyncd.conf /etc/
COPY ./helpers/docker/swift/bin /swift/bin
COPY ./helpers/docker/swift/misc/bashrc /swift/.bashrc
COPY ./helpers/docker/swift/rsyslog.d/10-swift.conf /etc/rsyslog.d/10-swift.conf
COPY ./helpers/docker/swift/misc/supervisord.conf /etc/supervisord.conf

RUN	pip install supervisor; mkdir /var/log/supervisor/ && \
    # create swift user and group
    /usr/sbin/useradd -m -d /swift -U swift && \
    sed -i 's/RSYNC_ENABLE=false/RSYNC_ENABLE=true/' /etc/default/rsync && \
    sed -i 's/SLEEP_BETWEEN_AUDITS = 30/SLEEP_BETWEEN_AUDITS = 86400/' /usr/local/src/swift/swift/obj/auditor.py && \
    chmod +x /swift/bin/* && \
    cp /usr/local/src/swift/test/sample.conf /etc/swift/test.conf && \
    sed -i 's/\$PrivDropToGroup syslog/\$PrivDropToGroup adm/' /etc/rsyslog.conf && \
    mkdir -p /var/log/swift/hourly; chown -R syslog.adm /var/log/swift; chmod -R g+w /var/log/swift && \
    mkdir -p /var/cache/swift; chown -R root:swift /var/cache/swift; chmod -R 775 /var/cache/swift && \
    echo swift:fingertips | chpasswd; usermod -a -G sudo swift && \
    echo %sudo ALL=NOPASSWD: ALL >> /etc/sudoers

EXPOSE 8080

CMD ["/bin/bash", "/swift/bin/launch.sh"]
