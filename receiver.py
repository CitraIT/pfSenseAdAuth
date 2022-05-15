#!/usr/local/bin/python3.8
# -*- coding: utf-8 -*-
import os
import sys
import signal
import socket
import re
dnsauth_path = '/var/unbound/dnsauth.conf'
basedomain = 'citrait.local'
filtergroupslist_path = '/usr/local/etc/e2guardian/lists/filtergroupslist' # user001=filter123

user_database = []

# load groups and users from e2guardian filtergroupslist
print(f'reading groups from e2guardian...')
filtergroupslist_file = open(filtergroupslist_path, 'r')
filtergroupslist_content = filtergroupslist_file.readlines()
filtergroupslist_file.close()
e2g_groups_database = {}
e2g_usergroups_database = {}
for line in filtergroupslist_content:
    user, group = line.strip().split('=')
    print(f'read user {user} member of group {group}')
    #e2g_groups_database.append((user,group))
    #search for group name and not reference...
    # /usr/local/etc/e2guardian: vim e2guardianf2.conf
    group_id = int(group.replace("filter",""))
    e2g_usergroups_database[user] =  group_id
    print(f'group {group} has id of {group_id}')
    print(f'searching for group name for group with id: {group_id}')
    with open(f'/usr/local/etc/e2guardian/e2guardianf{group_id}.conf','r') as filter_file:
        # ^groupname = 'grp'
        filter_lines = filter_file.readlines()
        for filter_line in filter_lines:
            if filter_line.startswith("groupname"):
                #print(f'{filter_line}')
                line_right = filter_line.split("=")[1].strip().replace("'","")
                if not group_id in e2g_groups_database.keys():
                    e2g_groups_database[group_id] =  line_right

print()

# debug
print(f'--- found the following groups -----')
for group_id, group_name in e2g_groups_database.items():
    print(f'group id: {group_id}, group name: {group_name}')
print()


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
    matches = re.findall('([0-9]{1,3}-[0-9]{1,3}-[0-9]{1,3}-[0-9]{1,3}).*\sTXT\s"(\w+),(\d+)"', line)
    if not matches:
        print(f'not matches for regex')
        continue
    ipaddr, user, group = matches[0]
    print(f'found user {user} ip {ipaddr} group {group}')
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
        user_group_id = e2g_usergroups_database.get(user)
        f.write(f'local-data: \'{ipaddr}.{basedomain} TXT "{user},{user_group_id}"\'\n')
        f.close()

        # signalling unbound to reload
        unbound_pid = 0
        with open("/var/run/unbound.pid","r") as pid_file:
            unbound_pid = int(pid_file.read())
            print(f'unbound is running under pid {unbound_pid}. signalling it to reload')
            os.kill(unbound_pid, signal.SIGHUP)

        print(f'mapping file updated!')
        print(f'---- database dump ----')
        for ipaddr,user in user_database:
            print(f'user: {user}\tip: {ipaddr}')


