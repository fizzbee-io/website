---
title: Enums, Records, and Collections
weight: -15
---

As with standard Python, FizzBee supports the standard sets, lists, and dictionaries. 
In addition to the standard sets and dictionaries where Python requires the types to be hashable, 
FizzBee also supports alternatives `genericset` and `genericmap` where the elements/keys can be
non-hashable types. 


{{< toc >}}

## Enums

To define an `enum`, Usually, these are defined at the top level.

{{% fizzbee %}}
Color = enum('RED', 'YELLOW', 'GREEN')

action Init:
  color = Color.RED

action Next:
  if color == Color.RED:
    color = Color.GREEN
  elif color == Color.GREEN:
    color = Color.YELLOW
  else:
    color = Color.RED
{{% /fizzbee %}}

To choose iterate over the enum values in `for` or `any`, you can simply use `dir()` builtin.

{{% fizzbee %}}
Color = enum('RED', 'YELLOW', 'GREEN')

action Init:
  color = Color.RED

action Next:
  any c in dir(Color):
    color = c
{{% /fizzbee %}}

{{% hint %}}
`enum` in FizzBee is only a syntactic sugar over the standard string. So
`Color.RED == 'RED'` is true. It is not a separate type, like Python's `enum.Enum`.

{{% /hint %}}

## Records

To define a `record`, These can be defined anywhere a standard python statement can be defined.

```python
# Define a record
msg = record(node=5, color=Color.RED, message='Hello')

# Access the fields
msg.node
# Set the fields
msg.color = Color.GREEN
```

## Immutable Struct
This may not be that useful, this comes with the Starlark language (that FizzBee is actually based on) so if needed use it.

```python
msg = struct(node=5, color=Color.RED, message='Hello')

msg.node = 10 # This will throw an error
```
As an implementation detail, the `enum` feature is implemented as a struct with keys as the enum values.

## Collections
### List
Ordered list of elements. Common standard Python operations are supported.
`append,clear,extend,index,insert,pop,remove`
```python
list = [1, 2, 3]
list[0] = 4
```

### Set
Unordered collection of unique elements. Common standard Python operations are supported.
`add,clear,difference,discard,intersection,issubset,issuperset,pop,remove,symmetric_difference,union`

```python

s = set([1, 2, 2])
# len(s) == 2
s.add(4)
# len(s) == 3
s.remove(2)
# len(s) == 2
```

### Dictionary
Key-value pairs. Common standard Python operations are supported.
`clear,get,items,keys,pop,popitem,setdefault,update,values`

```python

d = {1: 'one', 2: 'two'}

d[1] = 'uno'
```

### Generic Set
Unordered collection of unique elements. The elements can be non-hashable.
The standard methods like
`add,clear,difference,discard,intersection,issubset,issuperset,pop,remove,symmetric_difference,union`
are supported, and looping over the elements is also supported

```python

s = genericset()
s.add({'status': 'working', 'id': 1})
s.add({'status': 'pending', 'id': 2})
# len(s) == 2

# Adding the same element again does not change the size
s.add({'status': 'working', 'id': 1})
# len(s) == 2
```

### Generic Map
Key-value pairs. The keys can be non-hashable.
The standard methods like `clear,get,items,keys,pop,popitem,setdefault,update,values`
are supported, and looping over the elements is also supported.

```python

d = genericmap()
d[{'status': 'working', 'id': 1}] = 'one'
d[{'status': 'pending', 'id': 2}] = 'two'
```

### Bag
A bag is a collection of elements where duplicates are allowed.
The standard methods like `add,add_all,clear,discard,pop,remove` and looping over the elements are supported.

```python

b = bag()
b.add(1)
b.add(2)
b.add(2)
# len(b) == 3

print(b == bag([2, 1, 2])) # True Because, order of elements does not matter
print(b == bag([2, 1])) # False, because the number of '2' elements are different
```
