# ObjectScriber
`ObjectScriber` is a library for concise-ish serialization of simple-ish objects. 
`pickle` is a great serialization tool and it covers many cases, such as self recursive objects. 
However, due to this generality pickled objects are more bloated than they have to be.
`json` works great for nestings of primitive types, but doesn't work for user defined classes.
The goal of `ObjectScriber` (or `scriber` for short) is to serialize objects of 
*user defined classes which support objects of user defined classes as constructor arguments and are mutable post construction*.

# Examples
## Simplest Example
```
import objectscriber as scriber

@scriber.register_class
class A:
  def __init__(self, a):
    self.a = a
    
a = A(a="yo man") 
a_s = objectscriber.serialize(a) 
print (a_s)
```

Prints out: `{"class": "<class '__main__.A'>", "spec": {"kwargs": {"a": "yo man"}}}`. 

Unlike `pickle`, we have to register the base classes `scriber` can handle. Pickle pays the price for this in bloatiness.

So far, it's not that cool. It gets cooler.

## Scribing Children Classes
If we extend the previous example by adding the following:
```
class B(A): 
  def __init__(self, a1, a2):
    super().__init__(a1)
    self.b = a2
    
b = B(["list"], a)
b_s = scriber.serialize(b) 
print (b_s)
```

Prints out: `{"class": "<class '__main__.B'>", "spec": {"kargs": [["list"], {"class": "<class '__main__.A'>", "spec": {"kwargs": {"a": "yo man"}}}]}}`.

There are two cool things here: first, we didn't need to explicitly register class `B` 
with `scriber`. Because `B` inherits from `A`, it will automatically get registered and will be understood by
`scriber`. Second, constructor of the object `b` took a user defined object `a` as an argument. 

## Deserializing 
```
bb = scriber.deserialize(b_s) 
aa = scriber.deserialize(a_s) 
```

will reconstruct the objects back to their original form.

# Installation
`pip install objectscriber`

# Handling Mutable Objects
The basic version of scriber works by saving `kargs` and `kwargs` passed into the object constructor (initter to be more precise). 
If the object is changed after the initialization, the saved `kargs` and `kwargs` will no longer represent the up to date state
of the object. 

The way that this case is currently handled is by allowing registered classes to implement their own `serialize` and `deserialize` methods. Here's an example:

```
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
    
d = UserD() # the object has no soul during initialization
d.soul = 'has' # now it does
d_s = scriber.serialize(d) 
print (d_s) # output: {"class": "<class '__main__.UserD'>", "spec": "\"has\""}
dd = scriber.deserialize(d_s) 
print (dd.soul) # output: has
```

# Usecases in `corgie`

## Non-primitive Constructor Arguments
## Mutability
## Automatic Registration of Children
