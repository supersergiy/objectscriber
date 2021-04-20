import json
import six
import types

#TODO: check for recursive objects
#TODO: have a chache which will check if an object has been serialized before


class Scriber:
    def __init__(self):
        self.registered_classes = {
            "<class 'dict'>": dict
        }

    def clear(self):
        self.__init__()


    def register_class(self, cls, mutable=True):
        if str(cls) not in self.registered_classes:
            self.registered_classes[str(cls)] = cls

            # Automatically register children classes or the registered cls
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

            # Overwrite the __init__ function to save the args first
            def new_init(his_self, *kargs, **kwargs):
                # if already initialized, that means we're in super().__init__(..)
                if not hasattr(his_self, '__init_kargs__'):
                    his_self.__init_kargs__ = kargs
                    his_self.__init_kwargs__ = kwargs
                cls.__old_init__(his_self, *kargs, **kwargs)

            cls.__old_init__ = cls.__init__
            cls.__init__ = new_init

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
        if isinstance(obj, (bool, int, float, str)) or obj is None:
            result = obj
        elif isinstance(obj, list):
            result = []
            for v in obj:
                v_dict = self.to_dict(v)
                result.append(v_dict)
        elif isinstance(obj, dict):
            cls_str = str(type(obj))
            spec = dict()
            for k, v in obj.items():
                v_dict = self.to_dict(v)
                spec[k] = v_dict
            result = {
                    "class": cls_str,
                    "spec": spec
            }
        else:
            cls_str = str(type(obj))
            # TODO: fix this weird case
            if cls_str == "<class 'type'>":
                cls_str = str(obj)
            self._check_if_registered(cls_str, operation='serialize')

            if hasattr(obj, 'serialize'):
                spec = obj.serialize(self)
            else:
                spec = dict()
                spec['kargs'] = [self.to_dict(v) for v in obj.__init_kargs__]
                spec['kwargs'] = {
                    k: self.to_dict(v) for k, v in obj.__init_kwargs__.items()
                }
                if not spec['kargs']:
                    del spec['kargs']
                if not spec['kwargs']:
                    del spec['kwargs']

            result = {
                    "class": cls_str,
                    "spec": spec
            }

        return result

    def serialize(self, obj):
        obj_dict = self.to_dict(obj)
        return json.dumps(obj_dict)

    def dict_to_obj(self, d):
        if isinstance(d, (bool, int, float, str)) or d is None:
            return d
        elif isinstance(d, list):
            obj = [self.dict_to_obj(v) for v in d]
        else:
            cls_str = d['class']
            spec = d['spec']
            cls = self.get_class_from_str(cls_str, operation="deserialize")
            if cls == dict:
                obj = {k: self.dict_to_obj(v) for k, v in spec.items()}
            else:
                if hasattr(cls, "deserialize"):
                    obj = cls.deserialize(spec, self)
                else:
                    kargs = []
                    if 'kargs' in spec:
                        kargs = [self.dict_to_obj(v) for v in spec['kargs']]
                    kwargs = {}
                    if 'kwargs' in spec:
                        kwargs = {k: self.dict_to_obj(v) for k, v in spec['kwargs'].items()}
                    obj = cls(*kargs, **kwargs)
        return obj


    def deserialize(self, s):
        spec = json.loads(s)
        obj = self.dict_to_obj(spec)
        return obj
