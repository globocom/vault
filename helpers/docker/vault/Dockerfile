FROM python:2.7-stretch

RUN apt-get update \
    && apt-get clean all

RUN apt-get install -y build-essential libssl-dev default-libmysqlclient-dev \
                       python-pip python-dev

WORKDIR /home/app/vault

COPY . .

RUN pip install -r requirements_test.txt
