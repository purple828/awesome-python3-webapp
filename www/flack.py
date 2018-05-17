import orm
from models import User,Blog,Comment
import asyncio
import pymysql

async def test():

    #创建连接池,里面的host,port,user,password需要替换为自己数据库的信息
    await orm.create_pool(loop=loop, host='127.0.0.1', port=3306, user='root', password='123456aa',db='mysql')

    #没有设置默认值的一个都不能少
    u = User(name='fanglijuan', email='944974531@qq.com', passwd='0123', image='about:blank')
    await u.save()

# 获取EventLoop:
loop = asyncio.get_event_loop()

#把协程丢到EventLoop中执行
loop.run_until_complete(test())

#关闭EventLoop
loop.close()

# import mysql.connector
db = pymysql.connect('localhost','root','123456aa','mysql')

cur = db.cursor()
sql = 'select * from user1'
cur.execute(sql)
data = cur.fetchall()
print(data)

# conn=mysql.connector.connect(user='root', password='password', database='awesome')
# cursor=conn.cursor()
# cursor.execute('select * from users')
# data=cursor.fetchall()
# print(data)















def test():
    yield from orm.create_pool(user='root',password='123456aa',db='mysql')
    u = User(name='Test',email='fanglijuan@qq.com',passwd='123456',image='about:blank')
    yield from u.save()

for x in test():
    pass


# db = pymysql.connect("localhost","root","123456aa","mysql")