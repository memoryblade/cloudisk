from OpenSSL import *
from socket import *


ADDR = ('127.0.0.1',8001)

socket = socket(AF_INET,SOCK_STREAM)
ctx = SSL.Context(SSL.TLSv1_METHOD)
ctx.load_verify_locations('cacert.pem')

con = SSL.Connection(ctx,socket)

con.connect(ADDR)

con.send('hello')

data = con.recv(1024)

if data:
    print data

con.close()
socket.close()
