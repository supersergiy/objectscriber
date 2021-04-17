import objectscriber as scriber
import pickle
import codecs
import sys

@scriber.register_class
class A:
  def __init__(self, a):
    self.a = a

a = A(a="yo man")
a_s = scriber.serialize(a)
a_p = pickle.dumps(a, protocol=4)
a_p0 = pickle.dumps(a, protocol=0)
print (a_s) # {"class": "<class '__main__.A'>", "spec": {"kwargs": {"a": "yo man"}}}
print (len(a_s)) # 70
print (sys.getsizeof(a_s)) # 119
print (len(a_p)) # 93
print (sys.getsizeof(a_p)) # 126
print (len(a_p0)) # 158
print (sys.getsizeof(a_p0)) # 191

class B(A):
  def __init__(self, a1, a2):
    super().__init__(a1)
    self.b = a2

b = B(["list"], a)
b_s = scriber.serialize(b)
print (b_s)
