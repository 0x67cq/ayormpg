class Field(object):
    """
    用于映射数据库表的列的名字,类型和属性的基类
    Parameter:
        param name : column name
        param column_type : column_type
        param primary_key : (bool)is this column primary_key
        param foreign_key : (bool)is this column foreign_key
    Returns:
        None
    Raises:
        None
    """
    def __init__(self, name, column_type, primary_key, foreign_key,not_null):
        self.name = name
        self.column_type = column_type
        self.primary_key = primary_key
        self.foreign_key = foreign_key
        self.not_null = not_null

    def __str__(self):
        return '<%s, %s:%s>' % (self.__class__.__name__, self.column_type, self.name)

class IntegerField(Field):
    def __init__(self,name=None, primary_key=False, foreign_key=False, column_type='bigint', not_null=False):
        super(IntegerField, self).__init__(name,column_type,primary_key,foreign_key,not_null)

class FloatField(Field):
    def __init__(self, name=None, primary_key=False, foreign_key=False, column_type='double', not_null=False):
        super(FloatField,self).__init__(name,column_type,primary_key,foreign_key,not_null)

class StringField(Field):
    def __init__(self, name=None, primary_key=False, foreign_key=False, column_type='varchar(50)', not_null=False):
        super(StringField,self).__init__(name,column_type,primary_key,foreign_key,not_null)

class TextField(Field):
    def __init__(self, name=None, primary_key=False, foreign_key=False, column_type='text', not_null=False):
        super(TextField, self).__init__(name,column_type,primary_key,foreign_key,not_null)


class BooleanField(Field):
    def __init__(self, name=None, primary_key=None, foreign_key=False, column_type='boolean', not_null=False):
        super(BooleanField,self).__init__(name,column_type,primary_key,foreign_key,not_null)

class DateTimeField(Field):
    def __init__(self, name=None, primary_key=None, foreign_key=False, column_type='timestamp', not_null=False):
        super(DateTimeField,self).__init__(name,column_type,primary_key,foreign_key,not_null)

class PrimaryKey(object):
    """
    用于支持复合主键
    """
    def __init__(self,*args):
        self.li = args
