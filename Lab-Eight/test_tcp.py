import socket

# Connection options
import sys

import time


REMOTE_SERVER_HOSTNAME = '192.168.24.111'
LOCAL_SERVER_INTERFACE = ''
SERVER_PORT = 2050

# Data-size options
NUM_BLOCKS = 10000
BLOCK_SIZE = 1000

# Receiver options
PRINT_RESPONSE = True # Print each byte?
DO_WAIT = False # Wait between each byte?
WAIT_SECONDS = 1

def main():
    """ Provide the user with a variety of TCP-testing actions """

    # Get chosen operation from the user.
    action = input("Select an option from the menu below:\n"
                   "(1) send\n"
                   "(2) received\n"
                   "Please enter the option you want:\n")
    # Execute the chosen operation.
    if action in ['1', 'send']:
        send()
    elif action in ['2', 'receive']:
        receive()


def send():
    """
    Accept a connection from the client and send the client many X's.
    End with a Q.
    """
    server_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    server_socket.bind((LOCAL_SERVER_INTERFACE,SERVER_PORT))
    server_socket.listen(5)
    data_socket, client_address = server_socket.accept()

    for i in range(0,NUM_BLOCKS):
        data_socket.sendall(b'X' * BLOCK_SIZE)
    data_socket.sendall(b'Q')
    data_socket.close()
    print('Done sending message.')


def receive():
    """
    Receive many characters from the server.
    End with a Q.
    """
    client_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    client_socket.connect((REMOTE_SERVER_HOSTNAME,SERVER_PORT))

    byte = client_socket.recv(1)
    while byte != b'Q':
        if PRINT_RESPONSE:
            print(byte.decode())
        if DO_WAIT:
            time.sleep(WAIT_SECONDS)
        byte = client_socket.recv(1)
    client_socket.close()
    print('Done receiving message.')


def get_public_exponent(public_exponent, totient):
        totient = get_totient(p, q)
        public_exponent := 0
        r := n
        newt := 1
        newr := a
        while newr ≠ 0
            quotient := r
            div
            newr
            (public_exponent, newt) := (newt, public_exponent - quotient * newt)
            (r, newr) := (newr, r - quotient * newr)
        if r > 1 then return "a is not invertible"
        if t < 0 then public_exponent := public_exponent + totient
    return public_exponent

def get_totient(key_p, key_q):
    return (key_p - 1) * (key_q - 1)

main()