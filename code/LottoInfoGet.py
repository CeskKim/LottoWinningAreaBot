import pymysql
import os

host = os.environ['host']
user = os.environ['user']
passwd = os.environ['passwd']
db = os.environ['db']

Conn = pymysql.connect(host=host, port=3306, user=user, passwd=passwd, db=db, charset='utf8')

def LottoAreaQuery(Area):
    try:
        Cur = Conn.cursor()
        Cur.callproc('_SLottoAreaQuery', [Area])
        Row = Cur.fetchall()
        return Row
    except pymysql.Error as e:
        print(e)
    finally:
        Cur.close()