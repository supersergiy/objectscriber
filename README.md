# ObjectScriber
`ObjectScriber` is a library for concise-ish serialization of simple-ish objects. 
`pickle` is a great serialization tool and it covers many cases, such as self recursive objects. 
However, due to this generality pickled objects are more bloated than they have to be.
`json` works great for nestings of primitive types, but doesn't work for user defined classes.
The goal of `ObjectScriber` (or `scriber` for short) is to serialize objects of 
*user defined classes which support non-primitive constructor arguments and/or are mutable post construction*.

# Examples
## Simplest Example
```
import objectscriber as scriber

@scriber.register_class
class A:
  def __init__(self, a):
    self.a = a
    
a = A("yo man") 
a_s = objectscriber.serialize(a) 
print (a_s)
```

Prints out: `{"class": "<class '__main__.A'>", "spec": {"kargs": [{"class": "scriber.JSON", "spec": "yo man"}], "kwargs": {}}}`. 

Unlike `pickle`, we have to register the base classes `scriber` can handle. Pickle pays the price for this in bloatiness.

Our output is actually pretty bloaty itself, which could be optimized by more detailed handling of primitive classes. 
But so far, it's not that cool. It gets cooler.

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

Prints out: `{"class": "<class '__main__.B'>", "spec": {"kargs": [{"class": "scriber.JSON", "spec": ["list"]}, {"class": "<class '__main__.A'>", "spec": {"kargs": [{"class": "scriber.JSON", "spec": "yo man"}], "kwargs": {}}}], "kwargs": {}}}`.

Again, not super conscise. But there are two cool things: first, we didn't need to explicitly register class `B` 
with `scriber`. Because `B` inherits from `A`, it will automatically get registered and will be understood by
`scriber`. Second, constructor of the object `b` took a non-primitive object `a` as an argument. 

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

This can be handled in two ways. The first

# Usecases in `corgie`

## Automatic Registration of Children
## Non-primitive Constructor Arguments
## Mutability
