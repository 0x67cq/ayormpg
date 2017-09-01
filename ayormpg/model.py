import asyncio
import datetime
import logging
import asyncpg
from ayormpg.decorators import checkparam
from ayormpg.field import Field, IntegerField, StringField, DateTimeField

logger = logging.getLogger('asyncio')

logging.basicConfig(
    filename='app.log',
    level=logging.INFO
)


def log(sql):
    logger.info('SQL: %s' % sql)


async def setup_connection():
    """
    创建数据库连接池
    监听数据库连接数变化
    select * from pg_stat_activity;
    Args:
    Returns:
    Raises:
        RuntimeError('connect error')
    """
    global _pool
    _pool = None
    logger.info('create connect pool')
    _pool = await asyncpg.create_pool(user='guanchengqi', password='guanchengqi',
                                      database='guanchengqi', host='127.0.0.1')
    if not _pool:
        raise RuntimeError('connect error')
    return _pool


async def close_connection():
    """
    关闭数据库连接池
    """
    logger.info('close connect pool')
    await _pool.close()



@checkparam
async def select(sql, *args):
    """
    asyncpg查询接口封装
    Args:
        global _pool
        sql(str):
        args(list):
    Returns:
        a Recode object
    Raises:
    """
    async with _pool.acquire() as con:
        rs = await con.fetch(sql, *args)
        return rs



@checkparam
async def execute(sql, *args):
    """
    asyncpg执行接口封装
    Args:
        global _pool
        sql(str):
        args(list)
    Returns:
        a Record object
    Raises:
    """
    async with _pool.acquire() as con:
        rs = await con.execute(sql, *args)
        return rs


class ModelMetaclass(type):
    """
    Model元类,用于得到 用户定义的model子类中,自定义类的属性名和field子类的映射
    Args:
    Returns:
    Raises:
        RuntimeError('Primary Key Not Found')
        RuntimeError('Overflow Num of Primary Key')
    """
    def __new__(cls, name, bases, attrs):
        # abandon Model
        if name == 'Model':
            return type.__new__(cls, name, bases, attrs)
        table_name = name
        maps = {}
        not_null = []
        allow_null = []
        fields = []
        primary_key = None
        foreign_key = {}
        foreign_key_not_null = []
        serial = []
        unions = []
        if 'pk' in attrs.keys():
            primary_key = True
            attrs['__primary_key__'] = list(attrs['pk'].li)
        else:
            for k, v in attrs.items():
                if isinstance(v, Field):
                    maps[k] = v
                    if 'serial' == v.column_type:
                        serial.append(k)
                    if v.primary_key:
                        if primary_key:
                            raise RuntimeError('Overflow Num of Primary Key')
                        primary_key = k
                    else:
                        fields.append(k)
                    if not primary_key:
                        raise RuntimeError('Primary Key Not Found')
                    if v.union:
                        unions.append(k)
                    if v.not_null:
                        not_null.append(k)
                    else:
                        allow_null.append(k)
                    if v.foreign_key:
                        foreign_key[k] = str(v.foreign_key)
                    else:
                        pass

        for k in maps.keys():
            attrs.pop(k)
        for i in foreign_key.keys():
            if i in not_null:
                not_null.remove(i)
                foreign_key_not_null.append(i)
        tmp_not_null = []
        if primary_key in not_null:
            not_null.remove(primary_key)
        if primary_key in allow_null:
            allow_null.remove(primary_key)
        for i in not_null:
            tmp_not_null.append(i + ' ' + maps[i].column_type)
        tmp_allow_null = []
        for i in allow_null:
            tmp_allow_null.append(i + ' ' + maps[i].column_type)
        not_null = list(map(lambda f: '`%s`' % f, not_null))
        except_pk_fields = list(map(lambda f: '%s' % f, fields))
        attrs['__serial__'] = serial
        attrs['__foreign_key__'] = foreign_key
        attrs['__not_null__'] = not_null
        attrs['__maps__'] = maps
        attrs['__table_name__'] = table_name
        attrs['__primary_key__'] = primary_key
        attrs['__fields__'] = fields
        attrs['__select__'] = 'select %s, %s from %s' % (
            primary_key, ', '.join(except_pk_fields), table_name)
        attrs['__insert__'] = 'insert into %s (%s) values (%s)' % (
            table_name, create_insert_key(primary_key,serial,except_pk_fields) ,
            create_args_string(len(except_pk_fields)-(len(serial))+1))
        attrs['__update__'] = 'update %s set ' % (table_name,)
        attrs['__delete__'] = 'delete from %s where ?' % (table_name)
        attrs['__create__'] = 'CREATE TABLE %s (%s %s PRIMARY KEY %s%s%s%s)' % (
            table_name, primary_key, maps[primary_key].column_type,
            create_not_null(tmp_not_null), create_alow_null(tmp_allow_null),
            create_foreign_key_not_null(foreign_key,foreign_key_not_null,maps),
            create_union(unions)
        )
        return super(ModelMetaclass, cls).__new__(cls, name, bases, attrs)

def create_insert_key(primary_key,serial,except_pk_fields):
    """

    Args:
        primary_key(str):
        serial(list):
        except_pk_fields(list):

    Returns:

    """
    if not serial:
        lin = primary_key + ','+ ', '.join(except_pk_fields)
        return lin
    else:
        except_pk_fields.insert(0,str(primary_key))
        for i in serial:
            except_pk_fields.remove(i)
        return ', '.join(except_pk_fields)

def create_union(unions):
    """
    Args:
        unions(list):
    Returns:
    """
    if unions:
        return ', Unique({})'.format(' '.join(unions))
    else:
        return ''

def create_foreign_key_not_null(foreign_key,foreign_key_not_null,maps):
    """
    Args:
        foreign_key(list):
        tmp_foreign_key_not_null(list):

    Returns:
        highestStudent_id integer NOT NULL REFERENCES students(student_id)
    """
    if foreign_key_not_null:
        ret = []
        for i in foreign_key_not_null:
            ret.append(',' + i + ' ' + maps[i].column_type + ' NOT NULL' + ' '+ 'REFERENCES ' + foreign_key[i])
        return ('').join(ret)
    else:
        return ''

def create_alow_null(tmp_allow_null):
    """
    Args:
        tmp_allow_null(list):

    Returns:

    """
    if tmp_allow_null:
        return ',' + (',').join(tmp_allow_null)
    else:
        return ''
def create_not_null(tmp_not_null):
    """
    构造sql字符串
    Args:
        tmp_not_null(list):['age bigint']

    Returns:
        str:拼接用字符串NotNuLL

    """
    print('tmp_not_null',tmp_not_null)
    if  tmp_not_null:
        return ','+(' NOT NULL, ').join(tmp_not_null) + ' NOT NULL'
    else:
        return ''
def create_args_string(num) -> str:
    """
    构造占位符
    Args:
        num(int):
    Returns:
        str: like '$1,$2...'
    """
    l = []
    for n in range(num):
        l.append('$' + str(n + 1))
    return ', '.join(l)


class Model(dict, metaclass=ModelMetaclass):
    """
    元类映射结构,返回若干__attr__
    """
    def __init__(self, **kw):
        # logger.info(self.__create__)
        # logger.info(self.__update__)
        # logger.info(self.__delete__)
        # logger.info(self.__insert__)
        # logger.info(self.__select__)
        super(Model, self).__init__(**kw)

    def __getattr__(self, key):
        try:
            return self[key]
        except KeyError:
            raise AttributeError(r"'Model' object has no attribute '%s'" % key)

    def __setattr__(self, key, value):
        self[key] = value

    def get_primary_key(self, primary_val=None):
        """
        
        Args:
            primary_val():
        Returns:

        """
        """
        获取主键值，并处理为int类型
        Return:
            int
        """
        if not primary_val:
            primary_val = self.__get_value(self.__primary_key__)

        if isinstance(self.__maps__.get(self.__primary_key__), IntegerField):
            return int(primary_val)
        else:
            return primary_val

    def __get_value(self, key):
        """
        
        Args:
            key(str):
        Returns:

        """
        return getattr(self, key, None)

    def __get_value_or_default(self, key):
        """
        获取对象的属性对象的值,若无,使用default代替
        Args:
            key(str): 属性对象名
        Returns:
            str:属性值
        """
        value = getattr(self, key, None)
        if value is None:
            if key in self.__serial__:
                return ''
            field = self.__maps__[key]
            if field.default is not None:
                value = field.default() if callable(field.default) else field.default
                setattr(self, key, value)
        return value

    @classmethod
    async def all(cls):
        """
        find all objects
        Returns:
            a rocord object
            <Record id=1 email='boom@b.com' password='pd'>
        """
        sql = [cls.__select__]
        sql = ' '.join(sql)
        log('get' + sql)
        rs = await select(sql)
        return [cls(**r) for r in rs]

    @classmethod
    async def filter(cls, *args, **kw):
        """
        find objects by where statement
        Args:
            args:
            kw(dict): query kw
        Returns:[dict,]
        """
        sql = [cls.__select__]
        if kw:
            sql.append('where')
        if not args:
            args = []

        # 构造限定sql查询条件
        for index, key in enumerate(kw.keys()):
            if index == 0:
                sql.append(key + '=$1')
                args.append(kw.get(key))
            else:
                index += 1
                sql.append(' and ' + key + '=$' + str(index))
                args.append(kw.get(key))
        sql = ' '.join(sql)
        tmp = ''.join(str(args))
        log('filter' + sql + tmp)
        rs = await select(sql, *args)
        return [cls(**r) for r in rs]

    @classmethod
    async def get(cls, *args, **kw):
        """
        返回构造对象,属性是每条返回结果
        Returns:
            object: name=cls.__name__
        """
        sql = [cls.__select__]
        if kw:
            sql.append('where')
        if not args:
            args = []
        for index, key in enumerate(kw.keys()):
            index += 1
            sql.append(key + '=$' + str(index))
            args.append(kw.get(key))
        sql = ' '.join(sql)
        tmp = ''.join(str(args))
        log('get' + sql + tmp)
        res = await select(sql, *args)
        return [type(cls.__name__, (Model, ), cls(**r)) for r in res]

    @classmethod
    async def find_all(cls, where=None, *args, **kw):
        sql = [cls.__select__]
        if where:
            sql.append('where')
            sql.append(where)
        if args is None:
            args = []
        order_by = kw.get('order_by', None)
        if order_by:
            sql.append('order by')
            sql.append(order_by)
        limit = kw.get('limit', None)
        if limit is not None:
            sql.append('limit')
            if isinstance(limit, int):
                sql.append('?')
                args.append(limit)
            elif isinstance(limit, tuple) and len(limit) == 2:
                sql.append('?, ?')
                args.extend(limit)
            else:
                raise ValueError('Invalid limit value: %s' % str(limit))
        sql = ' '.join(sql)
        tmp = ''.join(str(args))
        log('find_all' + sql + tmp)
        rs = await select(sql, *args)
        return [cls(**r) for r in rs]

    @classmethod
    async def find_number(cls, selectField, where=None, args=None):
        """
        find number by select and where.
        Parameters:
            param selectField: 查询列
            param where:
            param args:
        Returns:
            int:某条结果的属性数量
        """
        sql = ['select %s _num_ from `%s`' % (selectField, cls.__table_name__)]
        if where:
            sql.append('where')
            sql.append(where)
        sql = ' '.join(sql)
        tmp = ''.join(str(args))
        log('findNum' + sql + tmp)
        rs = await select(sql, args, 1)
        if len(rs) == 0:
            return None
        return rs[0]['_num_']

    @classmethod
    async def find(cls, pk):
        """
        find object by primary key.
        Args:
            pk: primary_key
        Returns:
            dict:符合的条数
            or None
        """
        rs = await select('%s where `%s`=?' % (cls.__select__, cls.__primary_key__), [pk], 1)
        if len(rs) == 0:
            return None
        return cls(**rs[0])

    async def commit(self):
        """
        Returns:
        """
        args = list(map(self.__get_value_or_default, self.__fields__))
        args.insert(0, self.__get_value_or_default(self.__primary_key__))
        args.insert(0,'')
        args.insert(3,'')
        args =  [i for i in args if i != '']
        tmp = ''.join(str(args))
        log('commit ' + self.__insert__ + tmp)
        rows = await execute(self.__insert__, *args)
        if not rows:
            return False
        else:
            return True

    async def update(self):
        """
        update database row
        Returns:
        """
        try:
            primary_val = self.pop(self.__primary_key__)

            args = list(map(self.__get_value, self.keys()))
            args.append(self.get_primary_key(primary_val=primary_val))

            sql = self.__update__
            index = 0
            for index, key in enumerate(self.keys()):
                index += 1
                sql += key + '=$' + str(index) + ', '
            sql = sql[0:-2] + ' where id=$' + str(index + 1)
            tmp = ''.join(str(args))
            log('Update ' + str(sql) + tmp)
            rows = await execute(sql, *args)

            if rows == 'UPDATE 0':
                raise Exception('record not exits')
            elif rows == 'UPDATE 1':
                return True
            return False
        except Exception as e:
            raise Exception(e)

    @classmethod
    async def delete(cls, **kw):
        """

        Args:
            **kw(dict):删除符合条件
        Returns:
        Raises:
            ValueError("parameter should not be null")
            Exception('record not exits')
        """
        if not kw:
            raise ValueError("parameter should not be null")
        s = ''
        for k, v in kw.items():
            s = k + '=' + str(v)
        s = str(s)
        sql = cls.__delete__.replace('?', s)
        log('delete' + sql + s)
        rows = await execute(sql)
        if rows == 'DELETE 0':
            raise Exception('record not exits')
        elif rows == 'DELETE 1':
            return True
        return False

    @classmethod
    async def create(cls):
        """
        Create tables func
        Returns:
        Raises:
            RuntimeError('CREATE ERROR')
        """

        sql = cls.__create__
        log('create' + sql)
        status = await execute(sql)
        if 'CREATE TABLE' == status:
            pass
        else:
            raise RuntimeError('CREATE ERROR')


if __name__ == '__main__':
    class po(Model):
        id = IntegerField(primary_key=True)
        name = StringField()
        age = IntegerField(not_null=True)
        time = DateTimeField()

        @classmethod
        def pr(cls):
            print(cls.__maps__)
            print(cls.__not_null__)
            print(cls.__fields__)
            print(cls.__insert__)
            print(cls.__select__)
            print(cls.__update__)
            print(cls.__delete__)
            print(cls.__create__)

    async def main():
        await setup_connection()
        await po.create()
        p = po(id=2, name='popo', age=12, time=datetime.datetime(1984, 3, 1))
        await p.commit()
        p = po(id=2, name='bobo', age=13)
        await p.update()
        s = await po.filter(id=2, )
        s2 = await po.all()
        print(s)
        print(s2)
        await po.delete(id=2)

    po.pr()
    asyncio.get_event_loop().run_until_complete(main())
