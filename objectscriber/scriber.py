import json
import six

#TODO add different serialization strategies
#TODO: check for recursive objects
#TODO: have a chache which will check if an object has been serialized before
class ScriberException(Exception):
    pass

class EmptyClass:
    pass

class Scriber:
    def __init__(self):
        self.registered_classes = dict()

    def register_class(self, cls):
        self.registered_classes[str(cls)] = cls

        if not hasattr(cls, "serialize"):
            def serialize(obj):
                spec_dict = dict()
                for k, v in six.iteritems(obj.__dict__):
                    try:
                        v_serialized = {"class": "scriber.JSON", "spec": json.dumps(v)}
                    except (TypeError, OverflowError):
                        if not str(type(v)) in self.registered_classes
                            raise ScriberException("Cannot serialize a member object "
                                    " of class {}. {} is neither JSON-serializable nor "
                                    "registered with scriber. Use @scriber.register_class "
                                    "before class definition of {} in order to enable avoid "
                                    "this error".format(str(cls), str(cls), str(cls)))
                        else:
                            v. = v.serialize()
                            v_serialized = {"class": str(type(v)), "spec": v.serialize()}
                    spec_dict[k] = v_serialized
                return json.dumps(spec_dict)

            cls.serialize = serialize

        if not hasattr(cls, "deserialize"):
            def deserialize(s):
                obj = EmptyClass()
                params = json.loads(s)
                for k, v in six.iteritems(params):
                    v_dict = json.loads(v)
                    v_class_str = v_dict['class']
                    v_spec_str = v_dict['spec']

                    if v_class_str = "scriber.JSON":
                        v_deserialized = json.loads(v_spec_str)
                    else:
                        if v_class_str not in self.registered_classes:
                            raise ScriberException("Cannot deserialize a member object of "
                                    "class {}. {} is neither JSON-deserializable nor "
                                    "registered with scriber on the worker side. "
                                    "Use @scriber.register_class before class definition of {} "
                                    "and make sure the file in which it's defined gets imported "
                                    "on the worker side in order to avoid "
                                    "this error".format(str(cls), str(cls), str(cls)))
                        else:
                            v_cls = registeered_classes[v_dict['class']]
                            v_deserialized = v_cls.deserialize(v_dict['spec'])
                    obj.__dict__[k] = v_deserialized
                obj.__class__ = cls

            cls.deserialize = staticmethod(deserialize)
