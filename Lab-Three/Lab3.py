def next_byte():
    """
    Enter the byte in hexadecimal shorthand
    e.g.
      input a byte: e3

    :return: the byte as a bytes object holding one byte
    :author: Eric Nowac
    """

    msg = input('input a byte: ')
    return int(msg, 16).to_bytes(1, 'big')


def parseFileLength():
    """
    reads the first four bytes in the stream and converts it into and integer
    author = Sam
    :return: the number of lines in an integer
    """
    fileLength = b'';
    i = 0;
    while (i < 4):
        fileLength = fileLength + next_byte();
        i += 1;
    return int.from_bytes(bytes=fileLength, byteorder='big')


def parseLine():
    """
    reads teh next byte in the stream, then appends it to a byte object until ti reaches a newline character, then it
    decodes it into a string
    Author = Leah
    :return: the line as a string
    """
    nextByte = next_byte();
    lineMessage = b'';
    while(nextByte != b'\x0a'):
        lineMessage += nextByte
        nextByte = next_byte()
    lineMessage += b'\n'
    return lineMessage.decode()


def assembleMessage(fileLength, numFile):
    """
    Calls parseFileLength() and sets what is returned to an int fileLength. Calls parseLine() until there are
    no more lines while appending the lines to a string message.
    :return: a string of the message
    """

    message = "";
    for x in range(0, fileLength):
        message += parseLine();
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


fileLength = parseFileLength();
numFile = 0;

while(fileLength != 0):
    message, numFile = assembleMessage(fileLength);
    saveMessage(message, numFile);



