#!/usr/local/bin/python3.8
# -*- coding: utf-8 -*-
import os
import sys
import signal
import socket
import re
dnsauth_path = '/var/unbound/dnsauth.conf'
basedomain = 'citrait.local'

user_database = []

# load database on memory at startup
print(f'reading existing entries...')
f = open(dnsauth_path, 'r')
lines = f.readlines()
for line in lines:
    line = line.strip()
    if line == '':
        print(f'skipping empty line...')
        continue
    print(f'read line {line}')
    matches = re.findall('([0-9]{1,3}-[0-9]{1,3}-[0-9]{1,3}-[0-9]{1,3}).*\sTXT\s(\w+),\d+', line)
    if not matches:
        print(f'not matches for regex')
        continue
    ipaddr, user = matches[0]
    print(f'found user {user} ip {ipaddr}')
    user_database.append((ipaddr, user))
f.close()

if __name__ == '__main__':
    print(f'started listening on socket...')
    srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    srv.bind(('0.0.0.0', 8011))
    srv.listen(10)

    # Waiting for connections
    while True:
        client_socket, client_addr = srv.accept()
        print(f'nova conexao de {client_addr[0]}:{client_addr[1]}')
        data = client_socket.recv(1024).decode()
        print(f'received: {data}')
        client_socket.close()
        print(f'conexao encerrada.')

        # update mapping file with users
        print(f'updating mapping of users and ips')
        ipaddr, user = data.split(",")
        ipaddr = ipaddr.replace('.','-')


        # verify if the user already exists in the database
        if not (ipaddr, user) in user_database:
            print(f'user {user} with ip {ipaddr} not in database yet. adding it')
            user_database.append((ipaddr, user))
            print(f'user {user} added to database with ip {ipaddr}')
        else:
            print(f'entry for user {user} on ip {ipaddr} already in database. skipping it')
            continue

        # updating mapping file
        print(f'updatting map file')
        f = open(dnsauth_path, 'a')
        f.write(f'local-data: "{ipaddr}.{basedomain} TXT {user},1"\n')
        f.close()

        # signalling unbound to reload
        unbound_pid = 0
        with open("/var/run/unbound.pid","r") as pid_file:
            unbound_pid = int(pid_file.read())
            print(f'unbound is running under pid {unbound_pid}. signalling it to reload')
            os.kill(unbound_pid, signal.SIGHUP)

        print(f'mapping file updated!')
        print(f'---- database dump ----')
        for user, ipaddr in user_database:
            print(f'user: {user}\tip: {ipaddr}')


