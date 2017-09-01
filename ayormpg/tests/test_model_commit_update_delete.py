import unittest
import asyncio
import datetime
import random
import string
from ayormpg.model import  Model,setup_connection,close_connection
from ayormpg.field import IntegerField,StringField,DateTimeField,TextField


class Child(Model):
    id = IntegerField(primary_key=True, column_type='serial')
    name = StringField()
    age = IntegerField(not_null=True)
    birthday = DateTimeField()
    identification_number = IntegerField(not_null=True, union=True)

    @classmethod
    def pr(cls):
        print(cls.__foreign_key__)
        print(cls.__maps__)
        print(cls.__not_null__)
        print(cls.__fields__)
        print(cls.__insert__)
        print(cls.__select__)
        print(cls.__update__)
        print(cls.__delete__)
        print(cls.__create__)


class Student(Model):
    id = IntegerField(column_type='serial', primary_key=True)
    id_num = IntegerField(not_null=True, foreign_key='Child (identification_number)')
    talent = StringField(column_type='varchar(25)')
    like_eat = TextField()

    @classmethod
    def pr(cls):
        print(cls.__foreign_key__)
        print(cls.__maps__)
        print(cls.__not_null__)
        print(cls.__fields__)
        print(cls.__insert__)
        print(cls.__select__)
        print(cls.__update__)
        print(cls.__delete__)
        print(cls.__create__)
class TestModel(unittest.TestCase):
    def setUp(self):
        async def start():
            await setup_connection()
            Child.pr()
            Student.pr()
            await Child.create()
            await Student.create()

        asyncio.get_event_loop().run_until_complete(start())

    def test_commit(self):
        seed = "1234567890abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ!@#$%^&*()_+=-"

        sa = []
        for i in range(8):
            sa.append(random.choice(seed))
        salt = ''.join(sa)
        str = []
        str.append(salt)
        rdmstr0 = []
        for i in range(0, 10000):
            salt = ''.join(random.sample(string.ascii_letters + string.digits, 8))
            rdmstr0.append(salt)
        async def main():
            ch = Child(name='bob',age=12,birthday=datetime.datetime(1995,8,14),identification_number=23456332)
            ch2 = Child(name='koko',age=123,birthday=datetime.datetime(1897,9,1),identification_number=19872345)
            st = Student(id_num=23456332,talent='eat',like_eat='banana')
            st2 = Student(id_num=19872345,talent='read',like_eat='apple')
            await ch.commit()
            await ch2.commit()
            await st.commit()
            await st2.commit()
            # # update
            ch = Child(id=1,name='pop',age=12,birthday=datetime.datetime(1995,8,14),identification_number=23456332)
            await ch.update()
            # delete
            await Student.delete(id=2)
            await Child.delete(id=2)

        asyncio.get_event_loop().run_until_complete(main())

    def tearDown(self):
        async def end():
            await close_connection()
        asyncio.get_event_loop().run_until_complete(end())

