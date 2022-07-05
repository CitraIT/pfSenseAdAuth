#!/usr/local/bin/python3.8
# -*- coding: utf-8 -*-
import os
import sys
import signal
import socket
import re
from datetime import datetime

SOCK_BIND_ADDR = '0.0.0.0'
SOCK_BIND_PORT = 6544

LOG_FILE = '/var/log/adauth.log'

dnsauth_path = '/var/unbound/dnsauth.conf'
basedomain = 'citrait.local'
filtergroupslist_path = '/usr/local/etc/e2guardian/lists/filtergroupslist' # user001=filter123

user_database = []
e2g_groups_database = {}
e2g_usergroups_database = {}


# write_log()
# writes an entry in the main log
def write_log(line):
    log_file = open(LOG_FILE, 'a')
    timestamp = datetime.now()
    entry = str(timestamp)[:19] + " " + line + "\n"
    log_file.write(entry)
    log_file.close()



# load groups and users from e2guardian filtergroupslist
write_log(f'reading groups from e2guardian...')
filtergroupslist_file = open(filtergroupslist_path, 'r')
filtergroupslist_content = filtergroupslist_file.readlines()
filtergroupslist_file.close()
for line in filtergroupslist_content:
    user, group = line.strip().split('=')
    write_log(f'read user {user} member of group {group}')
    #e2g_groups_database.append((user,group))
    #search for group name and not reference...
    # /usr/local/etc/e2guardian: vim e2guardianf2.conf
    group_id = int(group.replace("filter",""))
    e2g_usergroups_database[user] =  group_id
    write_log(f'group {group} has id of {group_id}')
    write_log(f'searching for group name for group with id: {group_id}')
    with open(f'/usr/local/etc/e2guardian/e2guardianf{group_id}.conf','r') as filter_file:
        # ^groupname = 'grp'
        filter_lines = filter_file.readlines()
        for filter_line in filter_lines:
            if filter_line.startswith("groupname"):
                #print(f'{filter_line}')
                line_right = filter_line.split("=")[1].strip().replace("'","")
                if not group_id in e2g_groups_database.keys():
                    e2g_groups_database[group_id] =  line_right


# debug
write_log(f'--- found the following groups -----')
for group_id, group_name in e2g_groups_database.items():
    write_log(f'group id: {group_id}, group name: {group_name}')


# load database on memory at startup
write_log(f'reading existing entries...')
f = open(dnsauth_path, 'r')
lines = f.readlines()
for line in lines:
    line = line.strip()
    if line == '':
        write_log(f'skipping empty line...')
        continue
    write_log(f'read line {line}')
    matches = re.findall('([0-9]{1,3}-[0-9]{1,3}-[0-9]{1,3}-[0-9]{1,3}).*\sTXT\s"(\w+),(\d+)"', line)
    if not matches:
        write_log(f'not matches for regex')
        continue
    ipaddr, user, group = matches[0]
    write_log(f'found user {user} ip {ipaddr} group {group}')
    user_database.append((ipaddr, user))
f.close()




if __name__ == '__main__':
    # double fork magic for daemonise
    pid = os.fork()
    if pid != 0:
        sys.exit(0)
    os.setsid()
    pid = os.fork()
    if pid != 0:
        sys.exit(0)



    write_log(f'started listening on socket...')
    srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        srv.bind((SOCK_BIND_ADDR, SOCK_BIND_PORT))
    except OSError as e:
        write_log(str(e))
    srv.listen(10)

    # Waiting for connections
    while True:
        client_socket, client_addr = srv.accept()
        write_log(f'nova conexao de {client_addr[0]}:{client_addr[1]}')
        data = client_socket.recv(1024).decode()
        write_log(f'received: {data}')
        client_socket.close()
        write_log(f'conexao encerrada.')

        # update mapping file with users
        #print(f'updating mapping of users and ips')
        ipaddr, user = data.split(",")
        matches = re.findall('^[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}$', ipaddr)
        if not matches:
            write_log(f'invalid ip address {ipaddr}. skipping it.')
            continue
        ipaddr = ipaddr.replace('.','-')


        # verify if the user already exists in the database
        if not (ipaddr, user) in user_database:
            write_log(f'user {user} with ip {ipaddr} not in database yet. adding it')
            user_database.append((ipaddr, user))
            write_log(f'user {user} added to database with ip {ipaddr}')
        else:
            write_log(f'entry for user {user} on ip {ipaddr} already in database. skipping it')
            continue

        # updating mapping file
        write_log(f'updatting map file')
        f = open(dnsauth_path, 'a')
        user_group_id = e2g_usergroups_database.get(user)
        if user_group_id is None:
                write_log(f'invalid user group. skipping it!')
                continue
        f.write(f'local-data: \'{ipaddr}.{basedomain} TXT "{user},{user_group_id}"\'\n')
        f.close()

        # signalling unbound to reload
        unbound_pid = 0
        with open("/var/run/unbound.pid","r") as pid_file:
            unbound_pid = int(pid_file.read())
            write_log(f'unbound is running under pid {unbound_pid}. signalling it to reload')
            os.kill(unbound_pid, signal.SIGHUP)

        write_log(f'mapping file updated!')
        write_log(f'---- database dump ----')
        for ipaddr,user in user_database:
            write_log(f'user: {user}\tip: {ipaddr}')
