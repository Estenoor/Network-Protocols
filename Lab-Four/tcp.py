"""
- CS2911 - 0NN
- Fall 2019
- Lab N4
- Names: Leah Ersoy, Sam Ferguson
-

A simple TCP server/client pair.

The application protocol is a simple format: For each file uploaded, the client first sends four (big-endian) bytes indicating the number of lines as an unsigned binary number.

The client then sends each of the lines, terminated only by '\\n' (an ASCII LF byte).

The server responds with 'A' if it accepts the file, and 'R' if it rejects it.

Then the client can send the next file.
"""

# import the 'socket' module -- not using 'from socket import *' in order to selectively use items with 'socket.' prefix
import socket
import struct
import time

# Port number definitions
# (May have to be adjusted if they collide with ports in use by other programs/services.)
TCP_PORT = 12100

# Address to listen on when acting as server.
# The address '' means accept any connection for our 'receive' port from any network interface
# on this system (including 'localhost' loopback connection).
LISTEN_ON_INTERFACE = ''

# Address of the 'other' ('server') host that should be connected to for 'send' operations.
# When connecting on one system, use 'localhost'
# When 'sending' to another system, use its IP address (or DNS name if it has one)
# OTHER_HOST = '155.92.x.x'
OTHER_HOST = 'localhost'


def main():
    """
    Allows user to either send or receive bytes
    """
    # Get chosen operation from the user.
    action = input('Select "(1-TS) tcpsend", or "(2-TR) tcpreceive":')
    # Execute the chosen operation.
    if action in ['1', 'TS', 'ts', 'tcpsend']:
        tcp_send(OTHER_HOST, TCP_PORT)
    elif action in ['2', 'TR', 'tr', 'tcpreceive']:
        tcp_receive(TCP_PORT)
    else:
        print('Unknown action: "{0}"'.format(action))


def tcp_send(server_host, server_port):
    """
    - Send multiple messages over a TCP connection to a designated host/port
    - Receive a one-character response from the 'server'
    - Print the received response
    - Close the socket
    
    :param str server_host: name of the server host machine
    :param int server_port: port number on server to send to
    """
    print('tcp_send: dst_host="{0}", dst_port={1}'.format(server_host, server_port))
    tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp_socket.connect((server_host, server_port))

    num_lines = int(input('Enter the number of lines you want to send (0 to exit):'))

    while num_lines != 0:
        print('Now enter all the lines of your message')
        # This client code does not completely conform to the specification.
        #
        # In it, I only pack one byte of the range, limiting the number of lines this
        # client can send.
        #
        # While writing tcp_receive, you will need to use a different approach to unpack to meet the specification.
        #
        # Feel free to upgrade this code to handle a higher number of lines, too.
        tcp_socket.sendall(b'\x00\x00')
        time.sleep(1)  # Just to mess with your servers. :-)
        tcp_socket.sendall(b'\x00' + bytes((num_lines,)))

        # Enter the lines of the message. Each line will be sent as it is entered.
        for line_num in range(0, num_lines):
            line = input('')
            tcp_socket.sendall(line.encode() + b'\n')

        print('Done sending. Awaiting reply.')
        response = tcp_socket.recv(1)
        if response == b'A':  # Note: == in Python is like .equals in Java
            print('File accepted.')
        else:
            print('Unexpected response:', response)

        num_lines = int(input('Enter the number of lines you want to send (0 to exit):'))

    tcp_socket.sendall(b'\x00\x00')
    time.sleep(1)  # Just to mess with your servers. :-)  Your code should work with this line here.
    tcp_socket.sendall(b'\x00\x00')
    response = tcp_socket.recv(1)
    if response == b'Q':  # Reminder: == in Python is like .equals in Java
        print('Server closing connection, as expected.')
    else:
        print('Unexpected response:', response)

    tcp_socket.close()


def tcp_receive(listen_port):
    """
    - Listen for a TCP connection on a designated "listening" port
    - Accept the connection, creating a connection socket
    - Print the address and port of the sender
    - Repeat until a zero-length message is received:
      - Receive a message, saving it to a text-file (1.txt for first file, 2.txt for second file, etc.)
      - Send a single-character response 'A' to indicate that the upload was accepted.
    - Send a 'Q' to indicate a zero-length message was received.
    - Close data connection.
   
    :param int listen_port: Port number on the server to listen on
    """
    global LISTEN_ON_INTERFACE

    print('tcp_receive (server): listen_port={0}'.format(listen_port))
    listenSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM);
    listenSocket.bind((LISTEN_ON_INTERFACE, listen_port))
    # listening for connection
    listenSocket.listen(1)
    (data_socket, sender_address) = listenSocket.accept()
    print('sender_address:', sender_address)

    fileLength = parseFileLength(data_socket)
    fileNumber = 0
    while (fileLength != 0):
        message, fileNumber = assembleMessage(fileLength, fileNumber, data_socket)
        saveMessage(message, fileNumber)
        data_socket.sendall(b'A')
        fileLength = parseFileLength(data_socket)
    # While Loop Done

    data_socket.sendall(b'Q')
    time.sleep(1)  # Make sure Socket doesn't close while sending data
    data_socket.close()


def parseFileLength(data_socket):
    """
    reads the first four bytes in the stream and converts it into and integer
    author = Sam
    :return: the number of lines in an integer
    """
    fileLength = b'';
    i = 0;
    while (i < 4):
        fileLength = fileLength + next_byte(data_socket);
        i += 1;
    return int.from_bytes(bytes=fileLength, byteorder='big')


def parseLine(data_socket):
    """
    reads the next byte in the stream, then appends it to a byte object until ti reaches a newline character, then it
    decodes it into a string
    Author = Leah
    :return: the line as a string
    """
    nextByte = next_byte(data_socket);
    lineMessage = b'';
    while nextByte != b'\x0a':
        lineMessage += nextByte
        nextByte = next_byte(data_socket)
    lineMessage += b'\n'
    return lineMessage.decode()


def assembleMessage(fileLength, numFile, data_socket):
    """
    Calls parseFileLength() and sets what is returned to an int fileLength. Calls parseLine() until there are
    no more lines while appending the lines to a string message.
    :return: a string of the message
    """

    message = "";
    for x in range(0, fileLength):
        message += parseLine(data_socket);
    numFile += 1;
    return message, numFile


def saveMessage(message, numFile):
    # Open a file (like try-with-resources in Java)
    with open(str(numFile) + '.txt', 'wb') as output_file:
        # We are writing raw bytes (plain ASCII text) to the file
        # Since we opened the file in binary mode,
        # you must write a bytes object, not a str.
        output_file.write(message.encode())

        # You can call write multiple times to write more data. You need to explicitly add the newlines yourself, as in the example above.

    # The with open syntax guarantees the file will be closed. If you use a different
    # syntax, be sure to close it.
    # output_file.close()


def next_byte(data_socket):
    """
    Read the next byte from the socket data_socket.
   
    Read the next byte from the sender, received over the network.
    If the byte has not yet arrived, this method blocks (waits)
      until the byte arrives.
    If the sender is done sending and is waiting for your response, this method blocks indefinitely.
   
    :param data_socket: The socket to read from. The data_socket argument should be an open tcp
                        data connection (either a client socket or a server data socket), not a tcp
                        server's listening socket.
    :return: the next byte, as a bytes object with a single byte in it
    """
    return data_socket.recv(1)


# Invoke the main method to run the program.
main()
