FROM python:3.7

RUN apt-get update \
    && apt-get install -y build-essential libssl-dev default-libmysqlclient-dev python-pip python-dev \
    && apt-get -y clean all

WORKDIR /home/app/vault

COPY . .

RUN pip install -r requirements_test.txt
