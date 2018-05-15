import asyncio
import logging;logging.basicConfig(level=logging.INFO)
import aiomysql


@asyncio.coroutine
#创建连接池
def create_pool(loop,**kw):
    logging.info('create database connection pool')
    global __pool
    __pool = yield from aiomysql.create_pool(
        host = kw.get('host','localhost'),
        port = kw.get('port',3306),
        user = kw['user'],
        password = kw['password'],
        db = kw['db'],
        charset = kw.get('charset','utf-8'),
        autocommit = kw.get('autocommit',True),
        maxsize= kw.get('maxsize',10),
        minsize = kw.get('minsize',1),
        loop = loop
    )

#执行select语句
@asyncio.coroutine
def select(sql,args,size=None):
    logging.info(sql,args)
    global __pool
    with (yield from __pool) as conn:
        cur = yield from conn.cursor(aiomysql.DictCursor)
        yield from cur.execute(sql.replace('?','%s'),args or ())
        if size:
            rs = yield from cur.fetchmany(size)
        else:
            rs = yield from cur.fetchall()
        yield from cur.close()
        logging.info('rows return:%s'%len(rs))
        return rs

#要执行INSERT、UPDATE、DELETE语句，可以定义一个通用的execute()函数
@asyncio.coroutine
def execute(sql,args):
    logging.info(sql)
    with(yield from __pool) as conn:
        try:
            cur = yield from conn.cursor()
            yield from cur.execute(sql.replace('?',"%s"),args)
            affected = cur.rowcount
            yield from cur.close()
        except BaseException as e:
            raise
        return affected


