#!/usr/bin/env python
from socket import *
from OpenSSL import *
from time import ctime
from sql import dbHandler
import json
import sys
import threading
import tempfile

class mySSL:
    def __init__(self,host,port):
        self.BUFSIZ = 1024
        ADDR = (host,port)


        self.tcpSerSock = socket(AF_INET,SOCK_STREAM)
        ctx = SSL.Context(method=SSL.TLSv1_METHOD)
        ctx.use_certificate_file("server_cert.pem")
        ctx.use_privatekey_file("server_key.pem")
        print 'Checking Privatekey'
        ctx.check_privatekey()
        print 'passed'
        self.SerConn = SSL.Connection(ctx,self.tcpSerSock)

        self.SerConn.bind(ADDR)
        self.SerConn.listen(5)

    def __del__(self):
        self.SerConn.close()
        self.tcpSerSock.close()

class regSEQ(threading.Thread):
    def __init__(self):
        self.BUFSIZ=1024
        threading.Thread.__init__(self)
        pass

    def upFile(self):
        filename=self.fhead['filename'].split('\\')[-1]
        tmpfile=tempfile.TemporaryFile()
        filesize = long(self.fhead['filesize'])
        restsize = filesize
        while 1:
            if restsize > self.BUFSIZ:
                filedata = self.ClientConn.recv(self.BUFSIZ)
            else:
                filedata = self.ClientConn.recv(restsize)
            if not filedata: break
            tmpfile.write(filedata)
            restsize = restsize-len(filedata)
            if restsize == 0: break
        tmpfile.seek(0)

        self.dbhandler.uploadfile(filename,float(self.fhead['time']),self.userID,self.fhead['MD5'],tmpfile.read())

        tmpfile.close()

    def delFile(self):
       pass 

    def listFile(self):
        pass

    def run(self):
        myssl = mySSL("192.168.137.125",8001)
        while True:
            print 'waiting for connection...'
            self.ClientConn, fromaddr = myssl.SerConn.accept()
            print '...connected from:', fromaddr
            
            #data=ClientConn.recv(1024)
            self.fhead = json.loads(self.ClientConn.recv(1024))

            self.dbhandler=dbHandler()
            self.userID=self.dbhandler.isUserValid(self.fhead['username'],self.fhead['password'])
            if not self.userID:
                print 'Check your password!'
                self.ClientConn.close()
                continue

            seqType = self.fhead['type']
            if seqType == 'up':
                self.upFile()
            elif seqType == 'del':
                self.delFile()
            elif seqType == 'list':
                self.listFile()

            #ClientConn.send('[%s] %s' % (ctime(),data))
            #ClientConn.close()

class downSEQ(threading.Thread):
    def __init__(self):
        self.BUFSIZ=1024
        threading.Thread.__init__(self)
        pass
    def run(self):
        pass

def main():
    regseq=regSEQ()
    downseq=downSEQ()
    regseq.start()
    downseq.start()

    regseq.join()
    downseq.join()



if __name__=="__main__":
    main()

