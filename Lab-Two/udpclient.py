"""
- CS2911 - 0NN
- Fall 2017
- Lab N
- Names:
  (No need to put your name here since you do not need to submit the source files for this lab)

A simple UDP client.  Doesn't use an application protocol and just sends a text message as plain ASCII bytes
"""

import socket

print('Starting udpclient.py')

server_name = '192.168.24.96'
server_port = 2050 

client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

message = b'ACE\r\n'

client_socket.sendto(message, (server_name, server_port))

client_socket.close()