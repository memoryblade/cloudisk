import MySQLdb
import sys

class dbHandler:
    def __init__(self):
        self.conn=MySQLdb.connect(host='localhost',user='root',passwd='901030',db='cloudisk')
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

    def listfile(self,username):
        try:
            userID=self.isUserValid(username)

            if not userID:
                return None

            count = self.cur.execute('select filename, time from filetable where userID = %d' % userID)
            if count == 0:
                return None
            rows = self.cur.fetchall()
            return dict([(row[0],row[1]) for row in rows])
        except self.conn.Error,e:
            print 'Error %d: %s' % (e.args[0],e.args[1])
            sys.exit(1)

    def uploadfile(self,filename,time,userID,MD5,content):
        try:
            count=self.cur.execute('select time, MD5 from filetable where userID = %s and filename = %s',(userID,filename))
            if not count:
                query='insert into filetable (filename,time,userID,MD5,content) values ("%s",%f,"%s","%s",%%s)' % (filename,time,userID,MD5)
                print query
                f=open("test.jpg",'wb')
                f.write(content)
                f.close()
                self.cur.execute(query,content)
                self.dbcommit()
                return
            else:
                dbtime, dbMD5 = self.cur.fetchone()
                if MD5==dbMD5:
                    pass
                elif time-dbtime>0.01:
                    query='update filetable set MD5="%s", content="%%s" where userID="%s" and filename="%s"' % (MD5,userID,filename)
                    self.cur.execute(query,content)
                    self.dbcommit()

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
