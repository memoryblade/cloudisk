#!/usr/bin/env python
from socket import *
from OpenSSL import *
from time import ctime

def establishSSL(host,port):
    HOST = host
    PORT = port
    BUFSIZ = 1024
    ADDR = (HOST,PORT)


    tcpSerSock = socket(AF_INET,SOCK_STREAM)
    ctx = SSL.Context(method=SSL.TLSv1_METHOD)
    ctx.use_certificate_file("server_cert.pem")
    ctx.use_privatekey_file("server_key.pem")
    print 'Checking Privatekey'
    ctx.check_privatekey()
    print 'passed'
    SerConn = SSL.Connection(ctx,tcpSerSock)

    SerConn.bind(ADDR)
    SerConn.listen(5)

    #while True:
    print 'waiting for connection...'
    Conn, fromaddr = SerConn.accept()
    print '...connected from:', fromaddr
    
    return tcpSerSock, Conn
        #data = Conn.recv(BUFSIZ)
        #if not data:
        #    break
        #Conn.send('[%s] %s' % (ctime(),data))

        #Conn.close()
    #tcpSerSock.close()

def main():
    socket, conn = establishSSL("127.0.0.1",21577)
    data = conn.recv(1024)
    conn.send('[%s] %s' % (ctime(),data))
    conn.close()
    socket.close()


if __name__=="__main__":
    main()

