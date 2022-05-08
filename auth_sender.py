#!/usr/local/bin/python3.8
import socket

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(('localhost', 8011))
s.sendall(b'192.168.110.16,luciano')
s.close()


