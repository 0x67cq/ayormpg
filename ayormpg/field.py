class Field(object):
    """
    用于映射数据库表的列的名字,类型和属性的基类
    Args:
        name : column name
        column_type : column_type
        primary_key : (bool)is this column primary_key
        foreign_key : Reference other column
    Returns:
        None
    Raises:
        None
    """

    def __init__(
            self,
            name,
            column_type,
            primary_key,
            foreign_key,
            union,
            not_null,
            default):
        self.name = name
        self.column_type = column_type
        self.primary_key = primary_key
        self.foreign_key = foreign_key
        self.union = union
        self.not_null = not_null
        self.default = default

    def __str__(self):
        return '<%s, %s:%s>' % (self.__class__.__name__,
                                self.column_type, self.name)


class IntegerField(Field):
    def __init__(
            self,
            name=None,
            primary_key=False,
            foreign_key=None,
            union = False,
            column_type='bigint',
            not_null=False,
            default=0):
        super(
            IntegerField,
            self).__init__(
            name,
            column_type,
            primary_key,
            foreign_key,
            union,
            not_null,
            default)


class FloatField(Field):
    def __init__(
            self,
            name=None,
            primary_key=False,
            foreign_key=None,
            union = False,
            column_type='double',
            not_null=False,
            default=0.0):
        super(
            FloatField,
            self).__init__(
            name,
            column_type,
            primary_key,
            foreign_key,
            union,
            not_null,
            default)


class StringField(Field):
    def __init__(
            self,
            name=None,
            primary_key=False,
            foreign_key=None,
            union = False,
            column_type='varchar(50)',
            not_null=False,
            default=''):
        super(
            StringField,
            self).__init__(
            name,
            column_type,
            primary_key,
            foreign_key,
            union,
            not_null,
            default)


class TextField(Field):
    def __init__(
            self,
            name=None,
            primary_key=False,
            foreign_key=None,
            union = False,
            column_type='text',
            not_null=False,
            default=''):
        super(
            TextField,
            self).__init__(
            name,
            column_type,
            primary_key,
            foreign_key,
            union,
            not_null,
            default)


class BooleanField(Field):
    def __init__(
            self,
            name=None,
            primary_key = False,
            foreign_key=None,
            union = False,
            column_type='boolean',
            not_null=False,
            default=False):
        super(
            BooleanField,
            self).__init__(
            name,
            column_type,
            primary_key,
            foreign_key,
            union,
            not_null,
            default)


class DateTimeField(Field):
    def __init__(
            self,
            name=None,
            primary_key=False,
            foreign_key=None,
            union = False,
            column_type='timestamp',
            not_null=False,
            default='2017-08-29'):
        super(
            DateTimeField,
            self).__init__(
            name,
            column_type,
            primary_key,
            foreign_key,
            union,
            not_null,
            default)


class PrimaryKey(object):
    """
    用于支持复合主键
    """

    def __init__(self, *args):
        self.li = args
