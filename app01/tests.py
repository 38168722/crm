from django.test import TestCase

# Create your tests here.


def foo(x,y,**kwargs):
     print(x,y)
     print(kwargs) #{'c': 3, 'd': 4, 'f': 6} 吧多余的元素以字典的形式返回了
     print(*kwargs) #输出c d f ，就是把字典打散了

foo(1,y=2,c=3,d=4,f=6)