"""
- CS2911 - 0NN
- Fall 2017
- Lab N
- Names:Sam Ferguson, Leah Ersoy, Joe Bunales
-
-

A simple HTTP client
"""

# import the "socket" module -- not using "from socket import *" in order to selectively use items with "socket." prefix
import socket

# import showbits file for debugging purposes
import showbits

# import the "regular expressions" module
import re

# Address to listen on when acting as server.
# The address '' means accept any connection for our 'receive' port from any network interface
# on this system (including 'localhost' loopback connection).
LISTEN_ON_INTERFACE = ''


def main():
    """
    Tests the client on a variety of resources
    """

    # These resource request should result in "Content-Length" data transfer
    get_http_resource('http://msoe.us/CS/cs1.1curric.png', 'curric.png')

    # this resource request should result in "chunked" data transfer
    get_http_resource('http://msoe.us/CS/', 'index.html')

    # If you find fun examples of chunked or Content-Length pages, please share them with us!


def get_http_resource(url, file_name):
    """
    Get an HTTP resource from a server
           Parse the URL and call function to actually make the request.

    :param url: full URL of the resource to get
    :param file_name: name of file in which to store the retrieved resource

    (do not modify this function)
    """

    # Parse the URL into its component parts using a regular expression.
    url_match = re.search('http://([^/:]*)(:\d*)?(/.*)', url)
    url_match_groups = url_match.groups() if url_match else []
    #    print 'url_match_groups=',url_match_groups
    if len(url_match_groups) == 3:
        host_name = url_match_groups[0]
        host_port = int(url_match_groups[1][1:]) if url_match_groups[1] else 80
        host_resource = url_match_groups[2]
        print('host name = {0}, port = {1}, resource = {2}'.format(host_name, host_port, host_resource))
        status_string = make_http_request(host_name.encode(), host_port, host_resource.encode(), file_name)
        print('get_http_resource: URL="{0}", status="{1}"'.format(url, status_string))
    else:
        print('get_http_resource: URL parse failed, request not sent')


def make_http_request(host, port, resource, file_name):
    """
    Get an HTTP resource from a server

    :param bytes host: the ASCII domain name or IP address of the server machine (i.e., host) to connect to
    :param int port: port number to connect to on server host
    :param bytes resource: the ASCII path/name of resource to get. This is everything in the URL after the domain name,
           including the first /.
    :param file_name: string (str) containing name of file in which to store the retrieved resource
    :return: the status code
    :rtype: int
    """
    tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp_socket.connect((host, port))

    Action = b'GET'
    Version = b'HTTP/1.1'

    tcp_socket.sendall(Action + b' ' + resource + b' ' + Version + b'\r\n')  # sends the request to the host.
    tcp_socket.sendall(b'Host:' + b' ' + host + b'\r\n\r\n')

    statusCode = get_response_status(tcp_socket)
    headerDictionary = Get_Headers(tcp_socket)
    body = get_body(tcp_socket, headerDictionary)
    write_to_file(body, file_name)

    return int(statusCode)


def Get_Headers(socket):
    """
    Reads and Parses all of the headers in the http response
    :author: Sam
    :param socket:
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


def get_body(socket, headerDictionary):
    """
    Depending upon if the response has a content-length header or not this method returns
    the body of the response as a bytes object.
    Are the carriage return Line feeds apart of the data?
    author = Leah Ersoy
    :param socket: The socket to receive the response from.
    :param headerDictionary: A dictionary of the names of the headers.
    :return: body: bytes object with the body of the response from the server.
    """
    body = b''
    # if the message is chunked the body length will come back as -1
    # otherwise it will come back as a regular number.
    bodylength = get_length(headerDictionary)
    # if the message is chunked this executes
    if bodylength == -1:
        # reads length of chunk
        currentByte = next_byte(socket)
        chunkSizeBytes = b''
        while currentByte != b'\r':
            chunkSizeBytes += currentByte
            currentByte = next_byte(socket)

        next_byte(socket)  # read over the LF
        currentByte = b''  # Clears currentByte Variable for easier debugging

        sizeChunk = int(chunkSizeBytes, 16)  # converts chunk size bytes into int from base 16

        while sizeChunk != 0:  # continues as long as the size of the chunk isn't 0

            for i in range(0, sizeChunk):  # takes in the data of the chunk
                body = body + next_byte(socket)

            next_byte(socket)  # read over the CR
            next_byte(socket)  # read over the LF

            chunkSizeBytes = b''
            currentByte = next_byte(socket)
            while currentByte != b'\r':
                chunkSizeBytes += currentByte
                currentByte = next_byte(socket)

            next_byte(socket)  # read over the LF
            sizeChunk = int(chunkSizeBytes, 16) # converts chunk size bytes into int from base 16

    else:  # if the message has a content length
        for x in range(0, bodylength):  # takes in the data one byte at a time
            body = body + next_byte(socket)
    return body


def get_response_status(socket):
    """
    Reads the status line from the server and returns the decoded status code.
    author = Leah Ersoy
    :param socket: The socket to receive the response from.
    :return: responseStatus: The decoded status code from the server.
    """
    responseStatus = ''
    statusCode = b''
    currentByte1 = b''
    currentByte2 = b''
    while currentByte1 != b'\x20':
        currentByte1 = next_byte(socket)
    while currentByte2 != b'\x20':
        statusCode = statusCode + currentByte2
        currentByte2 = next_byte(socket)
    responseStatus = statusCode.decode('ASCII')

    # Finishes Reading Response Line so Header Dictionary Doesn't get Confused
    currentByte3 = b''
    while currentByte3 != b'\r':
        currentByte3 = next_byte(socket)
    next_byte(socket)

    return responseStatus


def get_length(header_dictionary):
    """
    Get the length of the file.
    If the file is chunked, return -1
    If nothing is found, return -1 as default
    author: Joe Bunales
    """

    if "Content-Length:" in header_dictionary:
        return int(header_dictionary["Content-Length:"])

    return -1


def write_to_file(contents, file_name):
    """
    This method uses a decoded message and writes it to the specified file.
    :param contents: The message to be written
    :param file_name: The name of the file the method is saving to
    """

    # Opens a file as an output file and writes to the specified file.
    with open(file_name, 'wb') as output_file:
        output_file.write(contents)
    output_file.close()


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


main()
