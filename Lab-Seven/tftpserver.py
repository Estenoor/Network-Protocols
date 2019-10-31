"""
- CS2911 - 031
- Fall 2019
- Lab 7
- Names:
  - Joe Bunales
  - Sam Ferguson
  - Leah Ersoy
A Trivial File Transfer Protocol Server
"""

# import modules -- not using "from socket import *" in order to selectively use items with "socket." prefix
import socket
import os
import math

# Helpful constants used by TFTP
TFTP_PORT = 69
TFTP_BLOCK_SIZE = 512
MAX_UDP_PACKET_SIZE = 65536


def main():
    """
    Processes a single TFTP request
    """

    client_socket = socket_setup()

    print("Server is ready to receive a request")

    ####################################################
    # Your code starts here                            #
    #   Be sure to design and implement additional     #
    #   functions as needed                            #
    ####################################################

    Process_Request(client_socket)

    ####################################################
    # Your code ends here                              #
    ####################################################

    client_socket.close()


def Read_Request_Message(client_socket):
    """
    Parses through the read request by the client and returns
    the information from the read request as a tuple bytes object.
    :author Leah
    :param client_socket:
    :return: tuple of the read request as bytes objects: op_code, filename, mode
    """
    requestPacket, requestAddr = read_packet(client_socket)
    op_code_1, requestPacket = next_byte(requestPacket)
    op_code_2, requestPacket = next_byte(requestPacket)
    op_code = int.from_bytes(op_code_1 + op_code_2, 'big')
    filename = b''
    counter1 = b''
    # continues to read the message until it reaches 00
    # this is the filename
    while counter1 != b'\x00':
        filename = filename + counter1
        counter1, requestPacket = next_byte(requestPacket)
    counter2 = b''
    mode = b''
    # continues to read the message until it reaches 00
    # this is the mode
    while counter2 != b'\x00':
        mode += counter2
        counter2, requestPacket = next_byte(requestPacket)
    # returns the important information from the read request
    return (op_code, filename.decode('ASCII'), mode.decode('ASCII')), requestAddr
  

def Read_Acknowledge(client_socket):
    """
    Goes through the acknowledge message and returns the
    block_number as an int
    author: Leah
    :param client_socket:
    :return: block_number: an int representing what block has been received
    """
    acknowledge_packet = read_packet(client_socket)
    op_code_1, acknowledge_packet = next_byte(acknowledge_packet)
    op_code_2, acknowledge_packet = next_byte(acknowledge_packet)
    op_code = int.from_bytes(op_code_1 + op_code_2, 'big')
    block_number = next_byte(acknowledge_packet) + next_byte(acknowledge_packet)
    block_number = int(block_number.decode('ASCII'))
    return block_number


def Process_Request(client_socket):
    request_message, request_addr = Read_Request_Message(client_socket)
    if request_message[0] == 1:  # If the Client is Requesting a file to be sent.
        file_name = './' + request_message[1]
        block_count = get_file_block_count(file_name)
        file_blocks = block_tuple(file_name, block_count)
        count = 0
        while count < block_count:
            ack = send_block(block_data=file_blocks[count],
                             block_number=count,
                             client_socket=client_socket,
                             client_addr=request_addr)
            if ack == count: # if the bock number acknowledge is the one sent
                count += 1

    elif request_message[0] == 2:  # If the Client is Sending a file
        pass


def send_block(block_data, block_number, client_socket, client_addr):
    """
    Sends block of file to client
    :param client_addr: address of the client
    :param block_data: data to be sent
    :param block_number: number of block being send
    :param client_socket: socket to send information on
    :return: the acknowledgment sent by the client.
    """
    message = block_number.to_bytes(length=2, byteorder='big')
    # print(type(block_data))
    message += block_data.to_bytes((block_data.bit_length() + 7) // 8, 'big')
    client_socket.sendto(message, client_addr)
    return Read_Acknowledge(client_socket)


def parse_blocks(file_name):
    """
    parses data to a tuple
    returns a tuple of 512 byte blocks
    finds and opens resources
    :param file_name: name of a file requested by a user

    :return: a tuple containing the blocks of data from a file

    author: Joe Bunales
    """
    contents = Get_Resource(file_name)
    block_count = get_file_block_count(file_name)
    return block_tuple(file_name, block_count)


# Helper Function for Getting the Resource
def Get_Resource(filename):
    """
    This method stores the contents of a file to a string to return in the header
    :param filename: name of the file to open and read
    :return: return the body of a file

    :author: Joe Bunales
    """
    File_Path = '.' + filename
    with open(File_Path, 'rb') as contents:
        body = contents.read()
    return body


def block_tuple(filename, block_count):
    """
    stores data to a tuple
    each spot in the tuple is a block of 512 bytes at maximum
    :param filename: name of a file requested by a user
    :param block_count: number of blocks of data to send to the user
    :return: a tuple containing the blocks of data

    author: Joe Bunales
    """
    # tuple to return
    tuple = ()
    # tuple to add to original tuple
    # add_tuple()
    for x in range(0, block_count):
        tuple = get_file_block(filename, block_count)
    return tuple


# Helper Functions for Reading Packets from Network
def next_byte(packet):
    """
    :author: Sam
    :param packet:
    :return:
    """
    # print(packet)
    packet = bytearray(packet)
    byte = packet[0].to_bytes(1, 'big')
    del packet[0]
    return byte, packet


def read_packet(client_socket):
    """
    :author: Sam
    :param client_socket:
    :return:
    """
    packet = client_socket.recvfrom(MAX_UDP_PACKET_SIZE)
    # print(packet)
    # print(packet[0])
    # print(packet[1])
    return packet[0], packet[1]


def get_file_block_count(filename):
    """
    Determines the number of TFTP blocks for the given file
    :param filename: THe name of the file
    :return: The number of TFTP blocks for the file or -1 if the file does not exist
    """
    try:
        # Use the OS call to get the file size
        #   This function throws an exception if the file doesn't exist
        file_size = os.stat(filename).st_size
        return math.ceil(file_size / TFTP_BLOCK_SIZE)
    except:
        return -1


def get_file_block(filename, block_number):
    """
    Get the file block data for the given file and block number
    :param filename: The name of the file to read
    :param block_number: The block number (1 based)
    :return: The data contents (as a bytes object) of the file block
    """
    file = open(filename, 'rb')
    block_byte_offset = (block_number - 1) * TFTP_BLOCK_SIZE
    file.seek(block_byte_offset)
    block_data = file.read(TFTP_BLOCK_SIZE)
    file.close()
    return block_data


def put_file_block(filename, block_data, block_number):
    """
    Writes a block of data to the given file
    :param filename: The name of the file to save the block to
    :param block_data: The bytes object containing the block data
    :param block_number: The block number (1 based)
    :return: Nothing
    """
    file = open(filename, 'wb')
    block_byte_offset = (block_number - 1) * TFTP_BLOCK_SIZE
    file.seek(block_byte_offset)
    file.write(block_data)
    file.close()


def socket_setup():
    """
    Sets up a UDP socket to listen on the TFTP port
    :return: The created socket
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind(('', TFTP_PORT))
    return s


####################################################
# Write additional helper functions starting here  #
####################################################


main()
