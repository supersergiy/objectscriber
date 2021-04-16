import json
import six
import types

#TODO add different serialization strategies
#TODO: check for recursive objects
#TODO: have a chache which will check if an object has been serialized before
#TODO: use ScribedObject type instead of dictionaries of class + spec

class ObjectscriberException(Exception):
    pass

class EmptyClass:
    pass

class Scriber:
    def __init__(self):
        self.registered_classes = {
            "<class 'dict'>": dict,
            "<class 'list'>": list
        }

    def register_class(self, cls):
        if str(cls) not in self.registered_classes:
            print (str(cls))
            self.registered_classes[str(cls)] = cls

            # Make it so that inhereting subclasses are
            # automatically registerd
            if not hasattr(cls, "__init_subclass__"):
                def __init_subclass__(subcls,  *kargs, **kwargs):
                    self.register_class(subcls)
                cls.__init_subclass__ = classmethod(__init_subclass__)
            else:
                #def __init_subclass__(*kargs, **kwargs):
                if hasattr(cls.__init_subclass__, '__text_signature') and \
                        cls.__init_subclass__.__text_signature__ is not None:
                    cls.__init_subclass_old__  = cls.__init_subclass__
                else:
                    def blank_fn(*args, **kwargs):
                        pass
                    cls.__init_subclass_old__ = blank_fn

                def __init_subclass__(subcls,  *kargs, **kwargs):
                    cls.__init_subclass_old__(subcls, *kargs, **kwargs)
                    self.register_class(subcls)

                cls.__init_subclass__ = classmethod(__init_subclass__)

        return cls

    def get_class_from_str(self, cls_str, operation="serialize/deserialize"):
        self._check_if_registered(cls_str, operation)
        return self.registered_classes[cls_str]

    def _check_if_registered(self, cls_str, operation):
        if cls_str not in self.registered_classes:
            raise ObjectscriberException("Cannot {} an "
                            "object of "
                            "class {}. {} is neither JSON-deserializable nor "
                            "registered with scriber on the worker side. "
                            "Use @scriber.register_class before class definition "
                            "of {} "
                            "and make sure the file in which it's defined gets "
                            "imported on the worker side in order to avoid "
                            "this error".format(operation,
                                                cls_str,
                                                cls_str,
                                                cls_str))


    def to_dict(self, obj):
        try:
            # is the object jsonifiable?
            json.dumps(obj)
            # if gotten past here without exception,
            # then the object is a dict of basic types
            obj_dict = {
                    "class": "scriber.JSON",
                    "spec": obj
            }
        except (TypeError, OverflowError) as e:
            # not JSON srializable objects
            print (obj, e)
            cls_str = str(type(obj))
            if cls_str == "<class 'type'>":
                import pdb; pdb.set_trace()
                cls_str = str(obj)
            self._check_if_registered(cls_str, operation='serialize')

            if hasattr(obj, "serialize"):
                spec = obj.serialize()
            else:
                if isinstance(obj, dict):
                    spec = dict()
                    for k, v in obj.items():
                        #if isinstance(obj, type):
                        print (type(obj))
                        import pdb; pdb.set_trace()
                        v_dict = self.to_dict(v)
                        spec[k] = v_dict
                elif isinstance(obj, list):
                    spec = list()
                    for v in obj:
                        if isinstance(obj, type):
                            import pdb; pdb.set_trace()
                        v_dict = self.to_dict(v)
                        spec.append(v_dict)
                else:
                    spec = dict()
                    for k, v in six.iteritems(obj.__dict__):
                        if not isinstance(obj, types.FunctionType):
                            v_dict = self.to_dict(v)
                            spec[k] = v_dict

            obj_dict = {
                    "class": cls_str,
                    "spec": spec
            }

        return obj_dict

    def serialize(self, obj):
        obj_dict = self.to_dict(obj)
        return json.dumps(obj_dict)

    def dict_to_obj(self, d):
        cls_str = d['class']
        spec = d['spec']

        if cls_str == "scriber.JSON":
            obj = spec
        else:
            cls = self.get_class_from_str(cls_str, operation="deserialize")
            if hasattr(cls, "deserialize"):
                obj = cls.deserialize(spec_str)
            else:
                obj = EmptyClass()
                for k, v in six.iteritems(spec):
                    v_deserialized = self.dict_to_obj(v)
                    obj.__dict__[k] = v_deserialized

                obj.__class__ = cls
        return obj


    def deserialize(self, s):
        spec = json.loads(s)
        obj = self.dict_to_obj(spec)
        return obj


