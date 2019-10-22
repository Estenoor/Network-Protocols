"""
- CS2911 - 0NN
- Fall 2017
- Lab N
- Names: Leah Ersoy, Sam Ferguson, Joe Bunales

A simple HTTP server
"""

import socket
import re
import threading
import os
import mimetypes
import datetime

# dictionary to hold all of the headers to be sent in a response.
responseHeaderDictionary = {};

def main():
    """ Start the server """
    http_server_setup(8080)


def http_server_setup(port):
    """
    Start the HTTP server
    - Open the listening socket
    - Accept connections and spawn processes to handle requests

    :param port: listening port number
    """

    num_connections = 10
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    listen_address = ('', port)
    server_socket.bind(listen_address)
    server_socket.listen(num_connections)
    try:
        while True:
            request_socket, request_address = server_socket.accept()
            print('connection from {0} {1}'.format(request_address[0], request_address[1]))
            # Create a new thread, and set up the handle_request method and its argument (in a tuple)
            request_handler = threading.Thread(target=handle_request, args=(request_socket,))
            # Start the request handler thread.
            request_handler.start()
            # Just for information, display the running threads (including this main one)
            print('threads: ', threading.enumerate())
    # Set up so a Ctrl-C should terminate the server; this may have some problems on Windows
    except KeyboardInterrupt:
        print("HTTP server exiting . . .")
        print('threads: ', threading.enumerate())
        server_socket.close()


def handle_request(request_socket):
    """
    Handle a single HTTP request, running on a newly started thread.

    Closes request socket after sending response.

    Should include a response header indicating NO persistent connection

    :param request_socket: socket representing TCP connection from the HTTP client_socket
    :return: None
    """

    Request_Line = Get_Request_Line(request_socket)
    Request_Headers = Get_Request_Headers(request_socket)

    if Request_Line[0] == 'GET':
        # Handle GET Requests Here
        Response_Headers = {}

    elif Request_Line[0] == 'PUT':
        # Handle PUT Requests Here
        Response_Headers = {}

    else:
        # Handle POST Requests Here
        Response_Headers = {}


def Get_Request_Line(request_socket):
    """
    Reads and returns the the request header as a tuple or array
    :param request_socket: the socket from which to read the request header from
    :return: Python Array Containing the information from the RequestHeader
    """
    Next_Byte = next_byte(request_socket)
    RequestHeaderByte = b''
    while Next_Byte != '\r':
        RequestHeaderByte += next_byte()
        Next_Byte = next_byte(request_socket)

    return Parse_Request_Line()


def Parse_Request_Line(RequestHeaderByte):
    """
    Parses Byte Object containing whole http request header
    :author: Sam
    :param RequestHeaderByte: The Bytes object containing the whole http request header
    :return: Python Tuple containing the request information from the request header
    """
    Request_Header = RequestHeaderByte.decode('ASCII')
    Request_Header_Values = Request_Header.split(' ')
    return Request_Header_Values


def Add_Response_Header(header_dictionary, header_name, header_value):
    """
    Adds a header to the dictionary to be sent in a response
    :author: Sam
    :param header_dictionary: The Dictionary to store the Header in.
    :param header_name: The name of the Header
    :param header_value: The Value of the Header
    :return: The dictionary with the new key,value set added.
    """

    header_dictionary[header_name] = header_value
    return header_dictionary

def Encode_Response_Headers(header_dictionary):
    """
    Combines all values in Python Dictionary to a single Byte Object
    :author: Sam
    :param header_dictionary: The Dictionary to Encode
    :return: The Bytes object containing all of the headers encoded for HTTP Transfer
    """
    encoded_dictionary = b''
    for key in header_dictionary:
        encoded_dictionary += key.encode()
        encoded_dictionary += b'\x20'
        encoded_dictionary += header_dictionary[key].encode()
        encoded_dictionary += b'\r\n'

    encoded_dictionary += b'\r\n'
    return encoded_dictionary


def Get_Request_Headers(socket):
    """
    Reads and Parses all of the headers in the http response
    :author: Sam
    :param socket: The Socket to read the Data From
    :return: dictionary containing header names and values in pairs
    """
    headers = {}
    (headerLength, rawHeader) = Get_Raw_Header(socket)

    while headerLength != 0:
        Header_Name = Get_Header_Name(rawHeader)
        Header_Value = Get_Header_Value(rawHeader)
        headers[Header_Name] = Header_Value
        (headerLength, rawHeader) = Get_Raw_Header(socket)

    return headers


def Get_Raw_Header(socket):
    """
    Reades the Raw Header data and records the length of the header
    :author: Sam
    :param socket:
    :return: (headerLength, header) length of header and the raw data of header
    """
    headerLength = 0
    header = b''
    currentByte = next_byte(socket)

    while currentByte != b'\r':
        header += currentByte
        headerLength += 1
        currentByte = next_byte(socket)

    next_byte(socket)
    return headerLength, header


def Get_Header_Name(rawHeader):
    """
    Gets Header Name From Raw Header Data
    :Author: Sam
    :param rawHeader:
    :return: The headers name
    """
    headerString = rawHeader.decode('ASCII')
    return headerString[0:headerString.find(' ')]


def Get_Header_Value(rawHeader):
    """
    Returns the Value tied to the header name.
    :Author: Sam
    :param rawHeader:
    :return:
    """
    headerString = rawHeader.decode('ASCII')
    return headerString[headerString.find(' '):len(headerString)]


def next_byte(data_socket: object) -> object:
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


# ** Do not modify code below this line.  You should add additional helper methods above this line.

# Utility functions
# You may use these functions to simplify your code.


def get_mime_type(file_path):
    """
    Try to guess the MIME type of a file (resource), given its path (primarily its file extension)

    :param file_path: string containing path to (resource) file, such as './abc.html'
    :return: If successful in guessing the MIME type, a string representing the content type, such as 'text/html'
             Otherwise, None
    :rtype: int or None
    """

    mime_type_and_encoding = mimetypes.guess_type(file_path)
    mime_type = mime_type_and_encoding[0]
    return mime_type


def get_file_size(file_path):
    """
    Try to get the size of a file (resource) as number of bytes, given its path

    :param file_path: string containing path to (resource) file, such as './abc.html'
    :return: If file_path designates a normal file, an integer value representing the the file size in bytes
             Otherwise (no such file, or path is not a file), None
    :rtype: int or None
    """

    # Initially, assume file does not exist
    file_size = None
    if os.path.isfile(file_path):
        file_size = os.stat(file_path).st_size
    return file_size


main()

# Replace this line with your comments on the lab
