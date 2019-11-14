import socket
import ssl
import pprint

hostname = 'https://expired.badssl.com/'

context = ssl.SSLContext(ssl.PROTOCOL_SSLv23)

# SSLv2 considered harmful.
context.options |= ssl.OP_NO_SSLv2

# SSLv3 has problematic security and is only required for really old
# clients such as IE6 on Windows XP
context.options |= ssl.OP_NO_SSLv3

# disable compression to prevent CRIME attacks (OpenSSL 1.0+)
context.options |= ssl.OP_NO_COMPRESSION

# verify certs and host name in client mode
context.verify_mode = ssl.CERT_REQUIRED
context.check_hostname = True

# Let's try to load default system
# root CA certificates for the given purpose. This may fail silently.
context.load_default_certs(ssl.Purpose.SERVER_AUTH)

with socket.create_connection((hostname, 443)) as sock:
    with context.wrap_socket(sock, server_hostname=hostname) as ssock:
        print(pprint.pformat(ssock.getpeercert()))
