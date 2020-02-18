FROM python:3.7

RUN apt-get update \
    && apt-get install -y build-essential libssl-dev default-libmysqlclient-dev python-pip python-dev \
    && apt-get -y clean all

COPY . /home/app/vault

RUN pip install -r /home/app/vault/requirements.txt

WORKDIR /home/app/vault
