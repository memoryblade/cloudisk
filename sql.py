#encoding=utf8
import MySQLdb
import json
import sys
import tempfile

class dbHandler:
    def __init__(self):
        self.conn=MySQLdb.connect(host='localhost',user='root',passwd='901030',db='cloudisk',charset='utf8')
        self.cur=self.conn.cursor()

    def __del__(self):
        self.cur.close()
        self.conn.close()

    def dbcommit(self):
        self.conn.commit()
        
    def isUserValid(self,username,password=None):
        if not password:
            count = self.cur.execute('select userID from user where username = %s',username)
        else:
            count = self.cur.execute('select userID from user where username = %s and password = %s',(username,password))
        if count == 0:
            print 'Error: no such user'
            return None
        else:
            return int(self.cur.fetchone()[0])

    def uploadfile(self,filename,filesize,time,userID,MD5,tempfile):
        try:
            count=self.cur.execute('select time, MD5 from filetable where userID = %s and filename = %s',(userID,filename))
            if not count:
                query='insert into filetable (filename,filesize,time,userID,MD5,content) values ("%s",%d,%f,"%s","%s",load_file("%s"))' % (filename,filesize,time,userID,MD5,tempfile)
                print query
                self.cur.execute(query)
                self.dbcommit()
                return
            else:
                dbtime, dbMD5 = self.cur.fetchone()
                if MD5==dbMD5:
                    pass
                elif time-dbtime>0.01:
                    query='update filetable set MD5="%s", content=load_file("%s"),time=%f,filesize=%d where userID="%s" and filename="%s"' % (MD5,tempfile,time,filesize,userID,filename)
                    self.cur.execute(query)
                    self.dbcommit()

        except self.conn.Error,e:
            print 'Error %d: %s' % (e.args[0],e.args[1])
            sys.exit(1)
            
    def deletefile(self,filename,userID):
        try:
            count=self.cur.execute('delete from filetable where userID = %s and filename = %s',(userID,filename))
            self.dbcommit()

        except self.conn.Error,e:
            print 'Error %d: %s' % (e.args[0],e.args[1])
            sys.exit(1)

    def listfile(self,userID):
        try:
            self.cur.execute('select filename,time,MD5,filesize from filetable where userID = %s' % userID)
            return json.dumps([{"filename":row[0],"time":row[1],"MD5":row[2],"filesize":row[3]} for row in self.cur.fetchall()])
            

        except self.conn.Error,e:
            print 'Error %d: %s' % (e.args[0],e.args[1])
            sys.exit(1)
    
    def downfile(self,filename,userID):
        try:
            count=self.cur.execute('select content from filetable where userID = %s and filename = %s',(userID,filename))
            if not count:
                print "no such file to download"
                return
            tmpfile=tempfile.TemporaryFile()
            tmpfile.write(self.cur.fetchone()[0])
            tmpfile.seek(0)
            return tmpfile

        except self.conn.Error,e:
            print 'Error %d: %s' % (e.args[0],e.args[1])
            sys.exit(1)        


    def test(self):
        print 'hi'

def main():
    dbhandler=dbHandler()
    #print (dbhandler.listfile('hlloworld'))
    print dbhandler.isUserValid('helloworld','123')

if __name__=="__main__":
    main()
