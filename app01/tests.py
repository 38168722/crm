from django.test import TestCase

# Create your tests here.

print("hello world")

class Foo(object):
    def __init__(self,data):
        self.data=data

    def __iter__(self):
        for item in self.data:
            yield item

user_list=[
    {"id":1,"name":"alex","age":19},
    {"id":2,"name":"jim","age":29}
]

obj = Foo(user_list)

for item in obj:
    print(item)