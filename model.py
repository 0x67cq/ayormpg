from field import  *
import asyncpg
import asyncio
async def setup_connection():
    '''
    创建数据库连接池
    监听数据库连接数变化
    select * from pg_stat_activity;
    :param app:
    :param loop:
    :return:
    '''
    global _pool
    _pool = await asyncpg.create_pool(user='guanchengqi', password='guanchengqi',
                                 database='guanchengqi', host='127.0.0.1')
    return _pool


async def close_connection():
    '''
    关闭数据库连接池
    '''
    await _pool.close()

# asyncpg查询接口封装
async def select(sql, *args, size=None):
    async with _pool.acquire() as con:
        rs = await con.fetch(sql, *args)
        return rs

# asyncpg执行接口封装
async def execute(sql, *args, autocommit=True):
    async with _pool.acquire() as con:
        rs = await con.execute(sql, *args)
        return rs

class ModelMetaclass(type):
    """
    Model元类,用于得到 用户定义的model子类中,自定义类的属性名和field子类的映射
    Parameter:
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
        primaryKey = None
        if 'pk' in attrs.keys():
            primaryKey = True
            attrs['__primary_key__'] =list(attrs['pk'].li)
        else:
            for k, v in attrs.items():
                if isinstance(v,Field):
                    maps[k] = v
                    if v.primary_key:
                        if primaryKey:
                            raise  RuntimeError('Overflow Num of Primary Key')
                        primaryKey = k
                    else:
                        fields.append(k)
                    if not primaryKey:
                        raise RuntimeError('Primary Key Not Found')
                    if v.not_null:
                        not_null.append(k)
                    else:
                        allow_null.append(k)
        for k in maps.keys():
            attrs.pop(k)
        # list每项加单引号
        tmp_not_null = []
        if primaryKey in not_null:
            not_null.remove(primaryKey)
        if primaryKey in allow_null:
            allow_null.remove(primaryKey)
        for i in not_null:
            tmp_not_null.append(i + ' ' + maps[i].column_type)
        tmp_allow_null = []
        for i in allow_null:
            tmp_allow_null.append(i + ' ' + maps[i].column_type)
        not_null = list(map(lambda f: '`%s`' % f, not_null))
        escaped_fields = list(map(lambda f: '%s' % f, fields))
        attrs['__not_null__'] = not_null
        attrs['__maps__'] = maps
        attrs['__table_name__'] = table_name
        attrs['__primary_key__'] = primaryKey  # 主键属性名
        attrs['__fields__'] = fields  # 除主键外的属性名
        # 构造默认的SELECT, INSERT, UPDATE和DELETE语句:
        # attrs['__select__'] = 'select `%s`, %s from `%s`' % (primaryKey, ', '.join(escaped_fields), table_name)
        # attrs['__insert__'] = 'insert into %s (%s, %s) values (%s)' % (table_name,
        #                 ', '.join(escaped_fields), primaryKey, create_args_string(len(escaped_fields)+1))
        # attrs['__update__'] = 'update `%s` set %s where `%s`=?' % (
        #     table_name, ', '.join(map(lambda f: '`%s`=?' % (maps.get(f).name or f), fields)), primaryKey)
        # attrs['__delete__'] = 'delete from `%s` where `%s`=?' % (table_name, primaryKey)
        attrs['__select__'] = 'select %s, %s from %s' % (primaryKey, ', '.join(escaped_fields), table_name)
        attrs['__insert__'] = 'insert into %s (%s,%s) values (%s)' % (
        table_name, primaryKey, ', '.join(escaped_fields), create_args_string(len(escaped_fields)+1))
        attrs['__update__'] = 'update %s set ' % (table_name,)
        attrs['__delete__'] = 'delete from %s where ?' % (table_name)
        attrs['__create__'] = 'CREATE TABLE %s (%s %s PRIMARY KEY, %s NOT NULL, %s)'%(
                                table_name, primaryKey, maps[primaryKey].column_type , (' NOT NULL, ').join(tmp_not_null),
                                (', ').join(tmp_allow_null)
                                )
        return super(ModelMetaclass,cls).__new__(cls, name, bases, attrs)

# 构造占位符
def create_args_string(num) -> str:
    L = []
    for n in range(num):
        L.append('$' + str(n+1))
    return ', '.join(L)

class Model(dict, metaclass=ModelMetaclass):
    def __init__(self, **kw):
        super(Model, self).__init__(**kw)

    def __getattr__(self, key):
        try:
            return self[key]
        except KeyError:
            raise AttributeError(r"'Model' object has no attribute '%s'" % key)

    def __setattr__(self, key, value):
        self[key] = value

    def get_primary_key(self, primary_val=None):
        '''
        获取主键值，并处理为int类型
        :return:
        '''
        if not primary_val:
            primary_val = self.__getValue(self.__primary_key__)

        if isinstance(self.__maps__.get(self.__primary_key__), IntegerField):
            return int(primary_val)
        else:
            return primary_val

    def __getValue(self, key):
        '''
        获取属性值
        :param key:
        :return:
        '''
        return getattr(self, key, None)

    def getValueOrDefault(self, key):
        value = getattr(self, key, None)
        if value is None:
            field = self.__maps__[key]
            if field.default is not None:
                value = field.default() if callable(field.default) else field.default
                setattr(self, key, value)
        return value

    @classmethod
    async def all(cls):
        '''
        find all objects
        :return:
        <Record id=1 email='boom@b.com' password='pd'>
        '''
        sql = [cls.__select__]
        rs = await select(' '.join(sql))
        return [cls(**r) for r in rs]

    @classmethod
    async def filter(cls, *args, **kw):
        '''
        find objects by where clause
        :param args:
        :param kw: Query parameters
        :return:
        '''
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

        rs = await select(' '.join(sql), *args)
        return [cls(**r) for r in rs]

    @classmethod
    async def get(cls, *args, **kw):
        '''
        返回对象
        :param args:
        :param kw:
        :return:
        '''
        sql = [cls.__select__]
        if kw:
            sql.append('where')
        if not args:
            args = []

        # 用占位符构造查询条件
        for index, key in enumerate(kw.keys()):
            index += 1
            sql.append(key + '=$' + str(index))
            args.append(kw.get(key))

        res = await select(' '.join(sql), *args)
        # TODO 构建对象出错
        return [type(cls.__name__, (Model, ), cls(**r)) for r in res]

    @classmethod
    async def findAll(cls, where=None, *args, **kw):
        ' find objects by where clause. '
        sql = [cls.__select__]
        if where:
            sql.append('where')
            sql.append(where)
        if args is None:
            args = []
        orderBy = kw.get('orderBy', None)
        if orderBy:
            sql.append('order by')
            sql.append(orderBy)
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
        rs = await select(' '.join(sql), *args)
        return [cls(**r) for r in rs]

    @classmethod
    async def findNumber(cls, selectField, where=None, args=None):
        ' find number by select and where. '
        sql = ['select %s _num_ from `%s`' % (selectField, cls.__table__)]
        if where:
            sql.append('where')
            sql.append(where)
        rs = await select(' '.join(sql), args, 1)
        if len(rs) == 0:
            return None
        return rs[0]['_num_']

    @classmethod
    async def find(cls, pk):
        ' find object by primary key. '
        rs = await select('%s where `%s`=?' % (cls.__select__, cls.__primary_key__), [pk], 1)
        if len(rs) == 0:
            return None
        return cls(**rs[0])

    async def commit(self):
        args = list(map(self.getValueOrDefault, self.__fields__))
        args.insert(0, self.getValueOrDefault(self.__primary_key__))
        print(self.__insert__,args)

        rows = await execute(self.__insert__, *args)
        if not rows:
            return False
        else:
            return True

    async def update(self):
        try:
            primary_val = self.pop(self.__primary_key__)

            args = list(map(self.__getValue, self.keys()))
            args.append(self.get_primary_key(primary_val=primary_val))

            sql = self.__update__
            index = 0
            for index, key in enumerate(self.keys()):
                index += 1
                sql += key + '=$' + str(index) + ', '
            sql = sql[0:-2] + ' where id=$' + str(index+1)
            rows = await execute(sql, *args)

            if rows == 'UPDATE 0':
                raise Exception('record not exits')
            elif rows == 'UPDATE 1':
                return True
            return False
        except Exception as e:
            raise Exception(e)
    @classmethod
    async def delete(cls,**kw):
        if '' == kw:
            raise ValueError("parameter should not be null")
        s = ''
        for k, v in kw.items():
            s = k + '=' + str(v)
        s = str(s)
        sql = cls.__delete__.replace('?',s)
        print(sql)
        rows = await execute(sql)
        if rows == 'DELETE 0':
            raise Exception('record not exits')
        elif rows == 'DELETE 1':
            return True
        return False
    @classmethod
    async def create(cls):
        """
        创建表,差个结果反馈
        """
        sql = cls.__create__
        print(1)
        status = await execute(sql)
        if 'CREATE TABLE' == status:
            print('CREATE SUCCESS')
        else:
            raise RuntimeError('CREATE ERROR')




if __name__ == '__main__':
    class po(Model):
        id = IntegerField(primary_key=True)
        name = StringField()
        age = IntegerField(not_null=True)
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
        #await po.create()
        #p = po(id=2,name='popo',age=12)
        #await p.commit()
        p = po(id=2,name='bobo',age=13)
        await p.update()
        # s = await po.filter(id=2, )
        # s2 = await po.all()
        # print(s)
        # print(s2)
        #await po.delete(id=2)




    po.pr()
    asyncio.get_event_loop().run_until_complete(main())