---
title: Current Limitations
weight: 1000
---

FizzBee being a new system, that is continuously being improved up on.
* Building a python-like language is hard. 
* Building a formal methods model checker is hard.
* Building a formal methods language that's python-like is even harder.

But we do these, because we are frustrated by the current state of formal methods. That said,
FizzBee is a work in progress. There are some gotchas and limitations, some are 
temporary, some may not be addressed for a while.

I would list some of the common issues with the language implementation if you
expect it to be as good as Python itself. If you face any other issues, please raise
as issue on the [github page](https://github.com/fizzbee-io/fizzbee)

## Line numbers in error messages
Currently, the error messages in line numbers are obviously wrong. This will be worked
on next as a high priority.

## Fizz functions can be called only in a limited ways
Currently, fizz functions can be called only in the following ways:
```
[variable_name =] [role.]fizz_function_name([parameters])
```
That is,
```python
# top level functions
fizz_function_name(arg1, arg2) # zero or more args
# with return value
state = fizz_function_name(arg1, arg2 ) 

# functions within a role
replica.fizz_function_name(arg1, arg2) 
state = replica.fizz_function_name(arg1, arg2 ) 

```
For all other cases, fizz treats the entire expression as a regular python code,
and runs using starlark interpreter, that will not recognize the fizz functions.
So you will get an error like,
```
Error evaluating expr: filename.fizz:1:1: undefined: fizz_function_name
```
If you get this error, you might have to extract the local variables to a separate
statement. For example,

```python
# This will not work
if replica.fizz_function_name(arg1, arg2) == 1:
    pass

# This will work
state = replica.fizz_function_name(arg1, arg2)
if state == 1:
    pass

# This will not work.
replica[i].fizz_function_name(arg1, arg2)
# This will work
r = replica[i]
r.fizz_function_name(arg1, arg2)

```
That said, standard python functions like max, len etc will work as expected.
This limit applies only to the fizz functions.

## Extracting local variables in a separate statement might alter the behavior

This will be the most confusing part of the language design. Being an abstract model
that simulates data storage with in-memory variables, a bit of care is needed when
extracting local variables to a separate statement.

For example, consider the following code:
```python
action Init:
  var1 = 0
  var2 = 0

always assertion BothNever1:
  return var1 == 0 or var2 == 0

action SetVar1:
  if var2 == 0:
    var1 = 1
    
action SetVar2:
  if var1 == 0:
    var2 = 1
```

vs 

```python
action Init:
  var1 = 0
  var2 = 0

always assertion BothNever1:
  return var1 == 0 or var2 == 0
  
action SetVar1:
  if var2 == 0:
    var1 = 1
    
action SetVar2:
  local = var1
  if local == 0:
    var2 = 1
```

In the first case, the assertion will always pass. But in the second case, the assertion
will fail. This is because, imagining var1 and var2 are coming from a database.
When you extract the local variable, you are actually taking a snapshot of the database
field. And them there could be some context switching that could change the value of var1.

