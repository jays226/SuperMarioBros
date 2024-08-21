class Store:
    def __init__(self, account, name=[]):
        self.__account = account
        self.__name = name

    def __str__(self):
        return "Store: " + str(self.__account) + ": " + self.__name

    def is_larger(self,amount):
        return amount > self.__account

    def get_name(self):
        return self.__name

    def get_number(self):
        return self.__account

    def set_name(self, new_name):
        self.__name = new_name

a = Store('example',1)
# print(a.get_name())

l = [1, 2, 3]

import copy

x = [
    1,
    2,
    3,
    [4,5,6]
]
# z = x
# z.remove(1)
# print(x)
# print(z)


x = [
    1,
    2,
    3,
    [4,5,6]
]
# print(x)
# y = x.copy()
# y[3].append("hello")
# print(x)
# print(y)




# # z = copy.deepcopy(x)
# y[3].append(1)
# # y[3].append('d')
# print(x)









l = [
    (1,2,3),
    (4,5,6),
    [7,8,9]
]

d = {1:2,3:4,5:6}

for item in d.items():
    key = item[0]
    val = item[1]

# for key,val in d.items():
    

# for x,y,z, in l:
#     print(x, y, z)
#
# for item in l:
#     x=item[0]
#     y=item[1]
#     z=item[2]
#     print(x,y,z)

s = 'test'
print(s[1])
