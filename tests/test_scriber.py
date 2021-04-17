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


def are_same(x, y):
    try:
        if x is None:
            return y is None
        elif isinstance(x, (int, float, bool, str)):
            return x == y
        elif isinstance(x, dict):
            for k in x.keys():
                res = are_same(x[k], y[k])
                if not res:
                    return False

        elif isinstance(x, list):
            for i in range(len(x)):
                res = are_same(x[i], y[i])
                if not res:
                    return False

        elif isinstance(x, tuple):
            for i in range(len(x)):
                res = are_same(x[i], y[i])
                if not res:
                    return False


        else:
            for k in x.__dict__.keys():
                res = are_same(x.__dict__[k], y.__dict__[k])
                if not res:
                    return False
    except AttributeError:
        return False

    return True

def test_simple():
    a = A("a")
    a_s = scriber.serialize(a)
    a_d = scriber.deserialize(a_s)
    assert are_same(a, a_d)

def test_inheret():
    b = B(["list", "item", "item2"], a2="bbbbbb")
    b_s = scriber.serialize(b)
    b_d = scriber.deserialize(b_s)
    assert are_same(b, b_d)

def test_nested_argument():
    b = B(a1=["list", "item", "item2"], a2="bbbbbb")
    c = C({"key": 0}, ["v1", {"key": 1}], a3=b)
    c_s = scriber.serialize(c)
    c_d = scriber.deserialize(c_s)
    assert are_same(c, c_d)
    c_d.b = 0
    assert not are_same(c, c_d)

