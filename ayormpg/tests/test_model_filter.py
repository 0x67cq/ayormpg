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

        asyncio.get_event_loop().run_until_complete(start())

    def test_filter(self):
        async def main():
            print(await Child.filter(id=5))
            print(await Child.filter(age=12))
            print(await Child.filter(name="xkUb'"))
        asyncio.get_event_loop().run_until_complete(main())

    def tearDown(self):
        async def end():
            await close_connection()
        asyncio.get_event_loop().run_until_complete(end())

