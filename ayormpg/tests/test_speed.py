import asyncio
import random
import string
import time

from ayormpg.model import *

seed = "1234567890abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ!@#$%^&*()_+=-"

sa = []
for i in range(8):
    sa.append(random.choice(seed))
salt = ''.join(sa)
str = []
str.append(salt)
rdmstr0 = []
# rdmstr1 = []
# rdmstr2 = []
# rdmstr3 = []
for i in range(0,10000):
    salt = ''.join(random.sample(string.ascii_letters + string.digits, 4))
    rdmstr0.append(salt)
# for i in range(0,10000):
#     salt = ''.join(random.sample(string.ascii_letters + string.digits, 8))
#     rdmstr1.append(salt)
# for i in range(0,10000):
#     salt = ''.join(random.sample(string.ascii_letters + string.digits, 8))
#     rdmstr2.append(salt)
# for i in range(0,10000):
#     salt = ''.join(random.sample(string.ascii_letters + string.digits, 8))
#     rdmstr3.append(salt)


print('random str ok')

now = lambda : time.time()

start = now()
class Po(Model):
    id = IntegerField(primary_key=True)
    name = StringField()
    age = IntegerField(not_null=True)
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
class Bp(Model):
    ss = IntegerField(primary_key=True)
    kk = IntegerField(foreign_key='Po(id)',not_null=True)
    qq = IntegerField(not_null=True)
    #op = IntegerField()

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
class Child(Model):
    id = IntegerField(primary_key=True, column_type='serial')
    name = StringField()
    age = IntegerField(not_null=True)
    birthday = DateTimeField()
    identification_number = IntegerField(not_null=True, union=True)

async def main():
    await setup_connection()
    #await Po.create()
    #await Bp.create()

    # for i in range(0,10000):
    # p = Po(name=rdmstr0[i],age=i)
    # await p.commit()
    # p = Po(id=2,name='bobo',age=13)
    # await p.update()
    #     s = await po.filter(id=i)
    # s2 = await po.all()
    # print(s2)
    # await Po.delete()
    for i in range(0,100):
        ch = Child(name=rdmstr0[i],age=12,birthday=datetime.datetime(1995,8,14),identification_number=random.randint(100000, 9000000))
        await ch.commit()
    await close_connection()
# Po.pr()
# Bp.pr()
asyncio.get_event_loop().run_until_complete(main())
print('TIME: ', now() - start)


# coroutine0 = setup_connection()
# start = now()
#
# class User(Model):
#     __table__ = 'users'
#
#     id = IntegerField(primary_key=True,)
#     email = StringField(ddl='varchar(50)')
#     password = StringField(ddl='varchar(50)')
#
# loop = asyncio.get_event_loop()
# loop.run_until_complete(coroutine0)
#
# # 一万次读取测试
# for i in range(1,2):
#     # coroutine4 = User.filter(id=i, )
#     coroutine4 = User.all()
#     task = asyncio.ensure_future(coroutine4)
#     loop.run_until_complete(task)
#     #print(task.result())
#
# # 一万次插入测试
# # for i in range(0,10000):
# #     u = User(id=i, email=rdmstr0[i],username=rdmstr1[i],nickname=rdmstr2[i],password=rdmstr3[i])
# #     coroutine1 = u.save()
# #     loop.run_until_complete(coroutine1)

