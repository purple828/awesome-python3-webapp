import asyncio
import logging;logging.basicConfig(level=logging.INFO)
import aiomysql
import

def log(sql,args=()):
    logging.info('SQL:%s'%sql)

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
    log(sql,args)
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
    log(sql)
    with(yield from __pool) as conn:
        try:
            cur = yield from conn.cursor()
            yield from cur.execute(sql.replace('?',"%s"),args)
            affected = cur.rowcount
            yield from cur.close()
        except BaseException as e:
            raise
        return affected

#将数个数用逗号连接
def create_args_string(num):
    L =[]
    for i in range(num):
        L.append('?')
    return ', '.join(L)

class Field(object):
    def __init__(self,name,column_type,primary_key,default):
        self.name = name
        self.column_type = column_type
        self.primary_key = primary_key
        self.default = default

    def __str__(self):
        return '<%s, %s:%s>'%(self.__class__.__name__,self.column_type,self.name)

class StringField(Field):
    def __init__(self,name=None,primary_key=False,default=None,ddl='varchar(100'):
        super().__init__(name,ddl,primary_key,default)

class BooleanField(Field):
    def __init__(self,name=None,default = False):
        super().__init__(name,'boolean',False,default)

class IntegetField(Field):
    def __init__(self,name=None,primary_key=False,default=0):
        super().__init__(name,'bigint',primary_key,default)

class FloatField(Field):
    def __init__(self,name=None,primary_key=False,default=0.0):
        super().__init__(name,'real',primary_key,default)

class TextField(Field):
    def __int__(self,name=None,default=None):
        super().__init__(name,'text',False,default)

class ModelMetaclass(type):
    def __new__(cls,name,bases,attrs):
        if name =='Model':
            return type.__new__(cls,name,bases,attrs)
        tableName = attrs.get('__table__',None) or name
        logging.info('found model: %s(table: %s)'%(name,tableName))
        mappings = dict()
        fields = []
        primaryKey = None
        for k,v in attrs.items:
            if isinstance(v,Field):
                logging.info('  found mapping: %s ==> %s'%(k,v))
                mappings[k] = v
                if v.primary_key:
                    #找到主键
                    if primaryKey:
                        raise BaseException ('Duplicate primary key for field: %s'%k)
                    primaryKey = k
                else:
                    fields.append(k)
        if not primaryKey:
            raise BaseException('Primary key not found')
        for k in mappings.keys():
            attrs.pop(k)
        escaped_fields = list(map(lambda f: '`%s`' % f, fields))
        attrs['__mappings__'] = mappings  #保存属性和列的映射关系
        attrs['__table__'] = tableName
        attrs['__primary_key__'] =primaryKey #主键属性名
        # attrs['__field__']



