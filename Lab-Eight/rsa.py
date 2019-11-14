"""
- CS2911 - 0NN
- Fall 2017
- Lab N
- Names: Sam Ferguson, Joe Bunales, Leah Ersay

16-bit RSA
"""
import math
import random
import sys

# Use these named constants as you write your code
MAX_PRIME = 0b11111111  # The maximum value a prime number can have
MIN_PRIME = 0b11000001  # The minimum value a prime number can have 
PUBLIC_EXPONENT = 17  # The default public exponent


def main():
    """ Provide the user with a variety of encryption-related actions """

    # Get chosen operation from the user.
    action = input("Select an option from the menu below:\n"
                   "(1-CK) create_keys\n"
                   "(2-CC) compute_checksum\n"
                   "(3-VC) verify_checksum\n"
                   "(4-EM) encrypt_message\n"
                   "(5-DM) decrypt_message\n"
                   "(6-BK) break_key\n "
                   "Please enter the option you want:\n")
    # Execute the chosen operation.
    if action in ['1', 'CK', 'ck', 'create_keys']:
        create_keys_interactive()
    elif action in ['2', 'CC', 'cc', 'compute_checksum']:
        compute_checksum_interactive()
    elif action in ['3', 'VC', 'vc', 'verify_checksum']:
        verify_checksum_interactive()
    elif action in ['4', 'EM', 'em', 'encrypt_message']:
        encrypt_message_interactive()
    elif action in ['5', 'DM', 'dm', 'decrypt_message']:
        decrypt_message_interactive()
    elif action in ['6', 'BK', 'bk', 'break_key']:
        break_key_interactive()
    else:
        print("Unknown action: '{0}'".format(action))


def create_keys_interactive():
    """
    Create new public keys

    :return: the private key (d, n) for use by other interactive methods
    """

    key_pair = create_keys()
    pub = get_public_key(key_pair)
    priv = get_private_key(key_pair)
    print("Public key: ")
    print(pub)
    print("Private key: ")
    print(priv)
    return priv


def compute_checksum_interactive():
    """
    Compute the checksum for a message, and encrypt it
    """

    priv = create_keys_interactive()

    message = input('Please enter the message to be checksummed: ')

    hash = compute_checksum(message)
    print('Hash:', "{0:04x}".format(hash))
    cipher = apply_key(priv, hash)
    print('Encrypted Hash:', "{0:04x}".format(cipher))


def verify_checksum_interactive():
    """
    Verify a message with its checksum, interactively
    """

    pub = enter_public_key_interactive()
    message = input('Please enter the message to be verified: ')
    recomputed_hash = compute_checksum(message)

    string_hash = input('Please enter the encrypted hash (in hexadecimal): ')
    encrypted_hash = int(string_hash, 16)
    decrypted_hash = apply_key(pub, encrypted_hash)
    print('Recomputed hash:', "{0:04x}".format(recomputed_hash))
    print('Decrypted hash: ', "{0:04x}".format(decrypted_hash))
    if recomputed_hash == decrypted_hash:
        print('Hashes match -- message is verified')
    else:
        print('Hashes do not match -- has tampering occured?')


def encrypt_message_interactive():
    """
    Encrypt a message
    """

    message = input('Please enter the message to be encrypted: ')
    pub = enter_public_key_interactive()
    encrypted = ''
    for c in message:
        encrypted += "{0:04x}".format(apply_key(pub, ord(c)))
    print("Encrypted message:", encrypted)


def decrypt_message_interactive(priv=None):
    """
    Decrypt a message
    """

    encrypted = input('Please enter the message to be decrypted: ')
    if priv is None:
        priv = enter_key_interactive('private')
    message = ''
    for i in range(0, len(encrypted), 4):
        enc_string = encrypted[i:i + 4]
        enc = int(enc_string, 16)
        dec = apply_key(priv, enc)
        if dec >= 0 and dec < 256:
            message += chr(dec)
        else:
            print('Warning: Could not decode encrypted entity: ' + enc_string)
            print('         decrypted as: ' + str(dec) + ' which is out of range.')
            print('         inserting _ at position of this character')
            message += '_'
    print("Decrypted message:", message)


def break_key_interactive():
    """
    Break key, interactively
    """

    pub = enter_public_key_interactive()
    priv = break_key(pub)
    print("Private key:")
    print(priv)
    decrypt_message_interactive(priv)


def enter_public_key_interactive():
    """
    Prompt user to enter the public modulus.

    :return: the tuple (e,n)
    """

    print('(Using public exponent = ' + str(PUBLIC_EXPONENT) + ')')
    string_modulus = input('Please enter the modulus (decimal): ')
    modulus = int(string_modulus)
    return (PUBLIC_EXPONENT, modulus)


def enter_key_interactive(key_type):
    """
    Prompt user to enter the exponent and modulus of a key

    :param key_type: either the string 'public' or 'private' -- used to prompt the user on how
                     this key is interpretted by the program.
    :return: the tuple (e,n)
    """
    string_exponent = input('Please enter the ' + key_type + ' exponent (decimal): ')
    exponent = int(string_exponent)
    string_modulus = input('Please enter the modulus (decimal): ')
    modulus = int(string_modulus)
    return (exponent, modulus)


def compute_checksum(string):
    """
    Compute simple hash

    Given a string, compute a simple hash as the sum of characters
    in the string.

    (If the sum goes over sixteen bits, the numbers should "wrap around"
    back into a sixteen bit number.  e.g. 0x3E6A7 should "wrap around" to
    0xE6A7)

    This checksum is similar to the internet checksum used in UDP and TCP
    packets, but it is a two's complement sum rather than a one's
    complement sum.

    :param str string: The string to hash
    :return: the checksum as an integer
    """

    total = 0
    for c in string:
        total += ord(c)
    total %= 0x8000  # Guarantees checksum is only 4 hex digits
    # How many bytes is that?
    #
    # Also guarantees that that the checksum will
    # always be less than the modulus.
    return total


# ---------------------------------------
# Do not modify code above this line
# ---------------------------------------

def create_keys():
    """
    :author: Sam and Leah
    Create the public and private keys.

    :return: the keys as a three-tuple: (e,d,n)
    """
    (p, q) = get_keys(PUBLIC_EXPONENT)
    modulus = get_modulus(p, q)
    totient = get_totient(p, q)
    print(p, q)
    private_exponent = get_private_exponent(PUBLIC_EXPONENT, totient)
    return PUBLIC_EXPONENT, private_exponent, modulus


def get_modulus(key_p, key_q):
    """
    Takes in the p and q values and returns the modulus, n.
    :author: Leah
    :param key_p:
    :param key_q:
    :return: modulus
    """
    modulus = key_p * key_q
    return modulus


def get_keys(public_exponent):
    """
    Chooses a random number between the MAX_PRIME and the MIN_PRIME then continues to add 2
    to this random number until the number is prime and (the number - 1)%e != 0
    :author: Leah 
    :param public_exponent:
    :return: p, q
    """
    p = get_prime_number()
    q = get_prime_number()
    while p == q:
        q = get_prime_number()

    return p, q


def get_prime_number():
    """
    :author: leah
    gets a prime number that is also co-prime with the public_exponent
    :return: 
    """
    test_number = random.randint(MIN_PRIME, MAX_PRIME)
    if test_number % 2 == 0:
        test_number += 1

    while True:
        if not is_prime(test_number):
            test_number += 2

        else:
            if not is_coprime(test_number, PUBLIC_EXPONENT):
                test_number += 2

        return test_number


def is_prime(number):
    """
    :author: sam
    Checks if the number is prime
    :param number: number to check
    :return: true if number is prime, false if not
    """
    for x in range(3, number):
        remainder = number % x
        if remainder == 0:
            return False

    return True


def is_coprime(x, y):
    """
    checks if x is coprime with y
    :author: Sam
    :param x:
    :param y:
    :return: true if x is coprime with y or false if not
    """
    if (x) % y != 0:
        return True
    return False


def get_private_exponent(public_exponent, totient):
    """
    get private exponent for private key
    :author: Joe
    :param public_exponent:
    :param totient:
    :return:
    """
    t = 0
    r = totient
    newt = 1
    newr = public_exponent
    while newr != 0:
        quotient = r // newr
        (t, newt) = (newt, t - quotient * newt)
        (r, newr) = (newr, r - quotient * newr)

    if r > 1:
        return "a is not invertible"
    if t < 0:
        t = t + totient
    return t

    return public_exponent


def get_totient(key_p, key_q):
    """
    :author: Joe
    :param key_p:
    :param key_q:
    :return:
    """
    return (key_p - 1) * (key_q - 1)


def apply_key(key, m):
    """
    Apply the key, given as a tuple (e,n) or (d,n) to the message.

    This can be used both for encryption and decryption.

    :author: Sam
    :param tuple key: (e,n) or (d,n)
    :param int m: the message as a number 1 < m < n (roughly)
    :return: the message with the key applied. For example,
             if given the public key and a message, encrypts the message
             and returns the ciphertext.
    """
    return (m ** key[0]) % key[1]


def break_key(pub):
    """
    Break a key.  Given the public key, find the private key.
    Factorizes the modulus n to find the prime numbers p and q.

    You can follow the steps in the "optional" part of the in-class
    exercise.
    :author: Joe, Leah, Sam
    :param pub: a tuple containing the public key (e,n)
    :return: a tuple containing the private key (d,n)
    """
    key_broken = False
    message = 'test'
    # while not key_broken:
    (p, q) = factor_number(pub[1])
    totient = get_totient(p, q)
    private_exponent = get_private_exponent(pub[0], totient)
    private_key = private_exponent, pub[1]

    return private_exponent, pub[1]


def factor_number(number):
    """
    :author: Joe
    :param number:
    :return:
    """
    sqrt = int(math.sqrt(number)) + 1
    for x in reversed(range(0, sqrt)):
        if number % x == 0:
            return x, number // x

    return 0, 0


def mass_break_test():
    """
    function to mass test the break key function instead of running and manually testing the function repeatedly
    :return:
    """
    for i in range(0, 1000):
        key_set = create_keys()
        print(get_private_key(key_set))
        private_key = break_key(get_public_key(key_set))
        print(private_key)
        if private_key == get_private_key(key_set):
            print('True')

        else:
            print('False')


def test_key_creation():
    for x in range(0, 100):
        test_messages = {'Hello', 'Hello World!', 'Life, Death, and the Universe'}
        key_set = create_keys()
        for message in test_messages:

            pub = get_public_key(key_set)
            encrypted = ''
            for c in message:
                encrypted += "{0:04x}".format(apply_key(pub, ord(c)))

            priv = get_private_key(key_set)
            decrypted = ''
            for i in range(0, len(encrypted), 4):
                enc_string = encrypted[i:i + 4]
                enc = int(enc_string, 16)
                print(priv[0])
                print(type(enc), type(priv[0]))
                dec = apply_key(priv, enc)
                if dec >= 0 and dec < 256:
                    decrypted += chr(dec)

            if message == decrypted:
                print(key_set, '----', ' Message: ', message, 'Decrypted Message: ', decrypted, ' Result: True')
            else:
                print(key_set, '----', ' Message: ', message, 'Decrypted Message: ', decrypted, ' Result: False')

        print('----------------------------')


# Your code and additional functions go here. (Replace this line.)

# ---------------------------------------
# Do not modify code below this line
# ---------------------------------------


def get_public_key(key_pair):
    """
    Pulls the public key out of the tuple structure created by
    create_keys()

    :param key_pair: (e,d,n)
    :return: (e,n)
    """

    return (key_pair[0], key_pair[2])


def get_private_key(key_pair):
    """
    Pulls the private key out of the tuple structure created by
    create_keys()

    :param key_pair: (e,d,n)
    :return: (d,n)
    """

    return (key_pair[1], key_pair[2])


# main()

# test_key_creation()

mass_break_test()