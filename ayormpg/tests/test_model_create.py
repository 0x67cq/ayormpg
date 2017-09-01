import unittest
import asyncio
from ayormpg.model import Model,setup_connection,close_connection
from ayormpg.field import IntegerField,StringField,DateTimeField,TextField

class TestModel(unittest.TestCase):
    def setUp(self):
        async def start():
            global _pool
            _pool = await setup_connection()
        asyncio.get_event_loop().run_until_complete(start())


    def test_create(self):
        class Child(Model):
            id = IntegerField(primary_key=True, column_type='serial')
            name = StringField()
            age = IntegerField(not_null=True)
            birthday = DateTimeField()
            identification_number = IntegerField(not_null=True,union=True)

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
            id = IntegerField(column_type='serial',primary_key=True)
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
        async def main():
            Child.pr()
            Student.pr()
            await Child.create()
            await Student.create()


        asyncio.get_event_loop().run_until_complete(main())


    def tearDown(self):
        async def end():
            await close_connection()
        asyncio.get_event_loop().run_until_complete(end())

if __name__ == '__main__':
    unittest.main()