# ObjectScriber
`ObjectScriber` is a library for concise-ish serialization of simple-ish objects. 
`pickle` is a great serialization tool and it covers many cases, such as self recursive objects. 
However, due to this generality pickled objects are more bloated than they have to be.
`json` works great for nestings of primitive types, but doesn't work for user defined classes.
The goal of `ObjectScriber` (or `scriber` for short) is to serialize objects of 
*user defined classes which support objects of user defined classes as constructor arguments and are mutable post construction*.

# Examples
## Simplest Example
```python
import objectscriber as scriber

@scriber.register_class
class A:
  def __init__(self, a):
    self.a = a
    
a = A(a="yo man") 
a_s = objectscriber.serialize(a) 
print (a_s) # output: {"class": "<class '__main__.A'>", "spec": {"kwargs": {"a": "yo man"}}}
```

Unlike `pickle`, we have to register the base classes `scriber` can handle. Pickle pays the price for this in bloatiness.

So far, it's not that cool. It gets cooler.

## Scribing Children Classes
If we extend the previous example by adding the following:
```python
class B(A): 
  def __init__(self, a1, a2):
    super().__init__(a1)
    self.b = a2
    
b = B(["list"], a)
b_s = scriber.serialize(b) 
print (b_s) # output: {"class": "<class '__main__.B'>", "spec": {"kargs": [["list"], {"class": "<class '__main__.A'>", "spec": {"kwargs": {"a": "yo man"}}}]}}
```

There are two cool things here: first, we didn't need to explicitly register class `B` 
with `scriber`. Because `B` inherits from `A`, it will automatically get registered and will be understood by
`scriber`. Second, constructor of the object `b` took a user defined object `a` as an argument. 

## Deserializing 
```python
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

```python
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

Note the `serializer` arguments in the user defined `serialize` and `deserialize` methods. This object is passed in by the scriber and will help the methods to handle attributes with user defined classes.

# Usecases in `corgie`
## Non-primitive Constructor Arguments
In `corgie`, we like passing user defined classes as `__init__` arguments to our tasks. 
One example of this comes from the fact that in alignment, we deal with a large number of CloudVolume layers (image, multiple masks, multiple fields)
that correspond to the same dataset. Because of this, it is convenient to bundle up our CloudVolumes as is objects of `Stack` class. `corgie`'s `ComputeField` Task
initer takes in a source stack, a target stack, as well as a desgination layer for the task output. Being able to pass stacks as init argument directly simplifies the workflow and makes the code a little more pretty.

## Mutability
The initial `Stack` is usually defined based on the user input, but can later be modyfied by the job to include more layers. For example, a see-through and see-through-stop masks can be added to the stack during block alignment. To correctly serialize stacks, it includes custom serialize and deserialize functions:

```python
    def serialize(self, serializer):
        spec = {}
        spec['name'] = self.name
        spec['layers'] = serializer.serialize(self.layers)
        spec['reference_layer'] = serializer.serialize(self.reference_layer)
        return spec


    @classmethod
    def deserialize(cls, spec, serializer):
        obj = cls()
        obj.name = spec['name']
        obj.layers = serializer.deserialize(spec['layers'])
        obj.reference_layer = serializer.deserialize(spec['reference_layer'])
        return obj
```

## Automatic Registration of Children
Because `corgie.Task`, `corgie.BaseLayer` and `corgie.BaseDataBackend` classes are registered with `scriber`, users can write new tasks, layer types and data backends without even knowing that `scriber` exists. 


## Extendability
Scriber also allows potentially nested tasks, which would allow for more complex logic. For example, we can bundle the `ComputeFieldTask` and `RenderTask` for the same bounding box into one task, or bundle all of the `ComputeFieldTask` for the vector voting job.  

## Comparison with `pickle`
All of the properties above can be achieved with `pickle`. However, `pickle` serialization is not space efficient. Also, `pickle` has some [known issues](https://github.com/uqfoundation/dill/issues/300) with inheritance. Overall, tasks serialized with `scriber` are 5-10 times smaller than tasks serialized with `pickle`.
