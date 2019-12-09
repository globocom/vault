FROM python:2.7-stretch

RUN apt-get update \
    && apt-get clean all

RUN apt-get install -y build-essential libssl-dev default-libmysqlclient-dev \
                       python-pip python-dev \
                       git telnet curl

RUN pip install pip --upgrade

WORKDIR /code

COPY requirements_test.txt requirements_test.txt

RUN pip install -r requirements_test.txt

COPY . .

CMD ["make", "run"]
