import objectscriber as scriber


@scriber.register_class
class A:
    def __init__(self, a):
        self.a = a

class B(A):
    def __init__(self, a1, a2):
        super().__init__(a1)
        self.b = a2

@scriber.register_class
class C:
    def __init__(self, a1, a2, a3):
        self.b = B(a1, a2)
        self.c = a3

def test_simple_1():
    a = A("a")
    b = B(["list"], "b")
    c = C({"key": 0}, ["v1", {"key": 1}], "MONEY")

    a_s = scriber.serialize(a)
    b_s = scriber.serialize(b)
    c_s = scriber.serialize(c)
    a_d = scriber.deserialize(a_s)
    b_d = scriber.deserialize(b_s)
    c_d = scriber.deserialize(c_s)

    def compare_vals(x, y):
        res = x == y
        print ("Tpyes: {},  {}".format(type(x), type(y)))
        print ("{} == {} -> {}".format(x, y, res))
        return  res

    def compare_obj(x, y):
        result = True
        for k in x.__dict__.keys():
            res = compare_vals(x.__dict__[k], y.__dict__[k])
            if not res:
                try:
                    res = compare_obj(x.__dict__[k], y.__dict__[k])
                except AttributeError:
                    result = False
                    break
        assert result == True
        return result

    compare_obj(a, a_d)
    compare_obj(b, b_d)
    compare_obj(c, c_d)
    #import pdb; pdb.set_trace()
    #c_d.b = 0
    compare_obj(c, c_d)

#print (a.a, a_d.a, type(a.a), type(a_d.a))
#print (b.a, b_d.a)
#print (b.b, b_d.b)
