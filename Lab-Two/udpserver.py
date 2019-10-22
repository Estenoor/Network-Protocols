"""
- CS2911 - 0NN
- Fall 2017
- Lab N
- Names:
  (No need to put your name here since you do not need to submit the source files for this lab)

A simple UDP server.  Doesn't use an application protocol and treats message body as plain ASCII bytes. Displays message with some statistics.
"""

import socket

print('Starting udpserver.py')

server_name = '' # When this is blank, the server will listen on all interfaces.
server_port = 2050

server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_socket.bind((server_name,server_port))

message,clientAddress = server_socket.recvfrom(1500) # 1500 is maximum packet size for UDP

print('Message length:',len(message))
print('Message:', message)
print('Message as str:', message.decode())
