#!/usr/bin/env python
#encoding=utf8
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
        print 'Checking Privatekey',port
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
 

    def upFile(self):
        filename=self.fhead['filename'].split('\\')[-1]
        tmpfile=tempfile.NamedTemporaryFile()
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

        self.dbhandler.uploadfile(filename,filesize,float(self.fhead['time']),self.userID,self.fhead['MD5'],tmpfile.name.replace("\\","/"))

        tmpfile.close()

    def delFile(self):
        filename=self.fhead['filename'].split('\\')[-1]
        self.dbhandler.deletefile(filename,self.userID)
        
        
    def run(self):
        myssl = mySSL("",8001)
        package=0
        while True:
            #try:
                #myssl = mySSL("",8001) 
                #package=0
                print '(reg)waiting for connection...'
                self.ClientConn, fromaddr = myssl.SerConn.accept()
                print '(reg)...connected from:', fromaddr
            
                #data=ClientConn.recv(1024)
                print "Reg package No: %d" % package
                package+=1
                self.fhead = json.loads(self.ClientConn.recv(1024))
                print self.fhead
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

                self.ClientConn.close()
                #ClientConn.send('[%s] %s' % (ctime(),data))
                #ClientConn.close()
            #except:
               #pass 

class downSEQ(threading.Thread):
    SEQS={}
    myssl=mySSL("",8002)
    def __init__(self):
        self.BUFSIZ=1024
        threading.Thread.__init__(self)
        downSEQ.SEQS[id(self)]=self


    def __del__(self):
        pass

    def listFile(self):
        data=self.dbhandler.listfile(self.userID)
        self.ClientConn.send(data)

    def downFile(self):
        filename=self.fhead['filename'].split('\\')[-1]
        tmpfile=self.dbhandler.downfile(filename,self.userID)
        while True:
            filedata=tmpfile.read(self.BUFSIZ)
            if not filedata:
                break
            self.ClientConn.send(filedata)

        print "file download complete: %s" % filename
        tmpfile.close()

    def run(self):
        try:
            print '(down)waiting for connection...'
            self.ClientConn, fromaddr = self.myssl.SerConn.accept()
            print '(down)...connected from:', fromaddr
            package=0
            downSEQ().start()
            while True:
        
                #data=ClientConn.recv(1024)
                print "(",id(self), ")Down package No: %d" % package
                package+=1
                self.fhead = json.loads(self.ClientConn.recv(1024))

                self.dbhandler=dbHandler()
                self.userID=self.dbhandler.isUserValid(self.fhead['username'],self.fhead['password'])
                if not self.userID:
                    print "(",id(self), ")Check your password!"
                    continue

                seqType = self.fhead['type']
                if seqType == 'list':
                    self.listFile()
                elif seqType == 'down':
                    self.downFile()
        except:
            del downSEQ.SEQS[id(self)]

def main():
    regseq=regSEQ()
    downseq=downSEQ()
    regseq.start()
    downseq.start()

    regseq.join()
    downseq.join()



if __name__=="__main__":
    main()

