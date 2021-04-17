import objectscriber as scriber

@scriber.register_class
class UserD:
    def __init__(self):
        self.soul = None

    def serialize(self, serializer):
        return serializer.serialize(self.soul)

    @classmethod
    def deserialize(cls, s, serializer):
        result = cls()
        result.soul = serializer.deserialize(s)
        return result


d = UserD()
d.soul = 'has'
d_s = scriber.serialize(d)
print (d_s)
dd = scriber.deserialize(d_s)
print (dd.soul)
