#!/usr/bin/env python

import MySQLdb
from os import getenv
from sys import exit
from time import sleep


MAX_TRIES = getenv('VAULT_CREATE_DB_MAX_TRIES', 20)
INTERVAL = getenv('VAULT_CREATE_DB_INTERVAL', 5)
DB_HOST = getenv('VAULT_MYSQL_HOST', 'vault_db')


def run():
    connected = False
    attempt = 0

    while not connected and attempt < MAX_TRIES:
        try:
            db = MySQLdb.connect(host=DB_HOST, user='root')
            connected = True
            print('Database connected!')
        except MySQLdb.MySQLError:
            attempt += 1
            print('Database not connected. Trying again in {} seconds...'.format(INTERVAL))
            sleep(INTERVAL)

    if connected:
        c = db.cursor()
        try:
            c.execute('USE vault;')
            print('Database already exists!')
        except MySQLdb.MySQLError:
            print('Database does not exists. Creating...')
            c.execute('CREATE DATABASE vault DEFAULT CHARACTER SET utf8 DEFAULT COLLATE utf8_general_ci;')
            print('Database created!')

        exit(0)

    exit(1)


if __name__ == '__main__':
    run()
