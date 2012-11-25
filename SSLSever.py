#!/usr/bin/env python
from socket import *
from OpenSSL import *
from time import ctime
import struct
import json

HOST = '127.0.0.1'
PORT = 8001
BUFSIZE = 1024
ADDR = (HOST,PORT)
FILEINFO_SIZE=struct.calcsize('128s32sI8s')

tcpSerSock = socket(AF_INET,SOCK_STREAM)
ctx = SSL.Context(method=SSL.TLSv1_METHOD)
ctx.use_certificate_file("D:\\Crypt\\server_cert.pem")
ctx.use_privatekey_file("D:\\Crypt\\server_key.pem")
print 'Checking Privatekey'
ctx.check_privatekey()
print 'passed'
SerConn = SSL.Connection(ctx,tcpSerSock)

SerConn.bind(ADDR)
SerConn.listen(5)

while True:
    print 'waiting for connection...'
    conn, fromaddr = SerConn.accept()
    print '...connected from:', fromaddr
    
#    fhead = conn.recv(FILEINFO_SIZE)
#    filename,temp1,filesize,temp2=struct.unpack('128s32sI8s',fhead)
#    print filename.strip('\00'),len(filename),type(filename)
#    print filesize
    fhead_j = conn.recv(1024)
    fhead = json.loads(fhead_j)
    
#    filename = 'new_'+filename.strip('\00')
    
    name = "D:\\Crypt\\"+'new_' + fhead['filename'].split('\\')[-1]
    filesize = long(fhead['filesize'])
    print name
    fp = open(name,'wb')
    restsize = filesize
    while 1:
        if restsize > BUFSIZE:
            filedata = conn.recv(BUFSIZE)
        else:
            filedata = conn.recv(restsize)
        if not filedata: break
        fp.write(filedata)
        restsize = restsize-len(filedata)
        if restsize == 0: break
    fp.close()
 
    conn.close()
    
 
    print "Finished"
    
#    data = Conn.recv(BUFSIZ)
#    if not data:
#        break
#    Conn.send('[%s] %s' % (ctime(),data))

#    Conn.close()
#tcpSerSock.close()
