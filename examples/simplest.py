import objectscriber as scriber


@scriber.register_class
class A:
  def __init__(self, a):
    self.a = a

a = A("yo man")
a_s = scriber.serialize(a)
print (a_s)

class B(A):
  def __init__(self, a1, a2):
    super().__init__(a1)
    self.b = a2

b = B(["list"], a)
b_s = scriber.serialize(b)
print (b_s)
