FROM python:2.7-stretch

ENV VERSION=12.0.3

RUN set -x \
    && apt-get -y update \
    && apt-get install -y libffi-dev python-dev libssl-dev netcat \
                          default-libmysqlclient-dev \
    && apt-get -y clean all

RUN curl -fSL https://tarballs.openstack.org/keystone/keystone-${VERSION}.tar.gz -o keystone-${VERSION}.tar.gz \
    && tar xvf keystone-${VERSION}.tar.gz \
    && cd keystone-${VERSION} \
    && pip install -r requirements.txt \
    && PBR_VERSION=${VERSION} pip install . \
    && cp -r etc /etc/keystone \
    && cd - \
    && rm -rf keystone-${VERSION}*

COPY ./helpers/docker/keystone/keystone.conf /etc/keystone/keystone.conf
COPY ./helpers/docker/keystone/bootstrap_fn.sh /etc/bootstrap_fn.sh
COPY ./helpers/docker/keystone/bootstrap.sh /etc/bootstrap.sh
COPY ./helpers/docker/keystone/create_db.py /etc/create_db.py
COPY ./helpers/docker/keystone/requirements.txt /etc/requirements.txt
RUN pip install -r /etc/requirements.txt
RUN chown root:root /etc/bootstrap.sh && chmod a+x /etc/bootstrap.sh
RUN echo '127.0.0.1 vault_keystone' >> /etc/hosts

ENTRYPOINT ["/etc/bootstrap.sh"]
EXPOSE 5000 35357

# HEALTHCHECK --interval=10s --timeout=5s \
#   CMD curl -f http://localhost:5000/v3 2> /dev/null || exit 1; \
#       curl -f http://localhost:35357/v3 2> /dev/null || exit 1; \
