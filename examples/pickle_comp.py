import objectscriber as scriber
import pickle
import codecs
import sys
import zlib

@scriber.register_class
class A:
  def __init__(self, a):
    self.a = a

class A_pure:
  def __init__(self, a):
    self.a = a


a = A(a="yo man")
a_pure = A_pure(a="yo man")

a_s = scriber.serialize(a)
a_s_z =  codecs.encode(zlib.compress(a_s.encode()), "base64").decode()
a_p = pickle.dumps(a_pure, protocol=4)
a_p0 = pickle.dumps(a_pure, protocol=0)
a_p_z =  codecs.encode(zlib.compress(a_p), "base64").decode()
print (a_s) # {"class": "<class '__main__.A'>", "spec": {"kwargs": {"a": "yo man"}}}
print (len(a_s)) # 70
print (sys.getsizeof(a_s)) # 119
print (len(a_s_z)) # 70
print (len(a_p)) # 54
print (len(a_p_z)) # 54
print (sys.getsizeof(a_p)) # 87
print (len(a_p0)) # 106
print (sys.getsizeof(a_p0)) # 139



class B(A):
  def __init__(self, a1, a2):
    super().__init__(a1)
    self.b = a2

class B_pure(A_pure):
  def __init__(self, a1, a2):
    super().__init__(a1)
    self.b = a2


b = B(["list"], a)
b_pure = B(["list"], a)
b_s = scriber.serialize(b)
print (b_s)

b_p = pickle.dumps(b_pure, protocol=4)
b_p0 = pickle.dumps(b_pure, protocol=0)
print (b_s) # {"class": "<class '__main__.A'>", "spec": {"kwargs": {"a": "yo man"}}}
print (len(b_s)) # 70
print (sys.getsizeof(b_s)) # 119
print (len(b_p)) # 93
print (sys.getsizeof(b_p)) # 126
print (len(b_p0)) # 158
print (sys.getsizeof(a_p0)) # 191


