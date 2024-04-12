---
title: Two Phase Commit (Procedural)
weight: 10
---

{{< toc >}}

# Two Phase Commit (Procedural style implementation)

This is another implementation style in FizzBee to model the Two Phase Commit protocol.
[Previous post](/examples/two_phase_commit/) was in functional style like TLA+ with only atomic actions. This post is in procedural style,
closely resembling PlusCal or pseudocode.

For the details on the algorithm read through the previous post.

## Quick overview
Unlike TLA+, FizzBee allows non-atomic actions. This is useful when you want to model a sequence of steps in a single action.
Sequence of steps implies, between each step, there can be an yield point where the model checker can explore other interleavings.
And the thread can also crash at any point in the sequence, meaning the later steps may never get executed.

## Yield points
This is a key concept in FizzBee. It is a point in the execution where the model checker can explore other interleavings.
In FizzBee, the yield points are implicit, that is, between each step in a sequence, there is a yield point.
The lowest level at which yield points are defined is at the statement level.
That is, 
In standard python, this line is not atomic, there is a chance,
a might have been updated between read and writing.

```python
a = a+1
```

But in FizzBee, _this line is atomic_. 

If you really want to model having an yield point between the two, then you have to use a temporary variable.
```python
tmp = a
a = tmp + 1
```

### Serial/parallel steps
In the previous example, we used the keyword `atomic`. If you remove it
or if you explicitly set to `serial`, it will be sequential step with yield points.
 When applied to a block (or the function/action itself, it is the same as applying to the root block), 

```python
action MyAction:
  step1()
  step2()
  step3()
```
Similarly when `parallel` is set, it is parallel steps, they may happen in any order.

```python
parallel action MyAction:
  step1()
  step2()
  step3()
```

### Serial/parallel iterations
Similar to steps, for loops can be made serial by setting `serial` keyword (or not setting any keyword). 
Or set it to be parallel by using the `parallel` keyword.
 (Note: if the parent block is atomic, the nested blocks continue to be atomic, even if not explicitly set)

```python
action MyAction:
  # or you can ignore the keyword
  serial for i in range(10):
    step1()
```

```python
action MyAction:
  parallel for i in range(10):
    step1()
```

### Message passing
In this approach, the message passing is implicitly modelled as a function call.
The only difference is, it is a blocking call making it synchronous communication.

A message loss is modelled as a crash before or after the call depending on what you want to model.

**How to differentiate between a message passing vs helper function call?**

If the call happened in an atomic block, it is a helper function call.
If it is not atomic (serial/parallel), it is a helper function call.

{{% hint type="info" %}}
At present, the function call must be `atomic` even if the function implementation
does not have to be. So to model message loss you will have to model with a temp variable,

```python
# This is a temporary hack, this will be fixed soon.
serial:
  tmp = None
  atomic:
    tmp = send_message()
  status = tmp
```

In the future, this could simply be written as,
```python
serial:
    status = send_message()
```
The yield points would be after evaluating the parameters to the function call
and after the function call before setting the return variable.

{{% /hint %}}


## Implementation

### States
Same as in the previous example, without the msgs set.
Since message passing is a function call, we do not need to model the messages.

```python
action Init:
  tmState = 'init'
  rmState = {1: 'init', 2:'init'}
  tmPrepared = set([])
```

### Safety invariant
Same as before.

```python
always assertion ResMgrsConsistent:
  for rm1 in rmState:
    for rm2 in rmState:
      if rmState[rm1] == 'committed' and rmState[rm2] == 'aborted':
        return False
  return True
```

### Action
Here, we only have a single action, the entry point for the
two-phase commit protocol. Something like the client invokes a `Write` operation.

Every other steps we have are helper functions.


```python

action TmWrite:
  if tmState != 'init':
      return
  else:
    tmState = 'working'

  parallel for rm in rmState.keys():
    serial:  
      vote = RmPrepare(rm)

      if vote == 'prepared':
        tmPrepared.add(rm)
      elif vote == 'aborted':
        TmAbort()
        return

  if len(tmPrepared) == len(rmState):
    TMCommit()

```


{{% hint note %}}
Here also, we are modeling a single transaction. So, we have an extra guard to disallow additional
action invocations. For a real implementation, we should generate a transaction id, so
and maintain the states for each transactio id in a dictionary.
I'll leave it as an exercise, to keep this article short.
{{% /hint %}}

The above code will not work as we noted before about a pending change. For now, use a temp variable and an atomic nested block.

A temporary hack.

{{% highlight udiff %}}
@@ -7,14 +7,18 @@
 
   parallel for rm in rmState.keys():
     serial:  
-      vote = RmPrepare(rm)
+      vote = ""
+      atomic: 
+        vote = RmPrepare(rm)
 
       if vote == 'prepared':
         tmPrepared.add(rm)
       elif vote == 'aborted':
-        TmAbort()
+        atomic: 
+          TmAbort()
         return
 
   if len(tmPrepared) == len(rmState):
-    TMCommit()
+    atomic:
+      TMCommit()
 

{{% /highlight %}}

### Helper functions
Now we just need to implement each function one by one

#### RmPrepare
Sets the state to be one of prepared or aborted and returns the value.
Unlike, here the message passing is at most once, we don't need any guard clause.

```python
func RmPrepare(rm):
  oneof:
    rmState[rm] = 'prepared'
    rmState[rm] = 'aborted'

  return rmState[rm]
```

#### Coordinator and Participant Abort

```python
func TmAbort():
  tmState = 'aborted'
  parallel for rm in rmState.keys():
    # This atomic is temporary, this will be fixed soon.
    atomic:
      RmAbort(rm)

func RmAbort(rm):
    rmState[rm] = 'aborted'

```

#### Coordinator and Participant Commit

```python
func TMCommit():
  tmState = 'committed'
  parallel for rm in rmState.keys():
    atomic:
      RmCommit(rm)

func RmCommit(rm):
    rmState[rm] = 'committed'

```

Here is the latest code so far.

{{% fizzbee %}}
always assertion ResMgrsConsistent:
  for rm1 in rmState.keys():
    for rm2 in rmState.keys():
      if rmState[rm1] == 'committed' and rmState[rm2] == 'aborted':
        return False
  return True

action Init:
  tmState = 'init'
  rmState = {1: 'init', 2:'init'}
  tmPrepared = set([])

action TmWrite:
  if tmState != 'init':
      return
  else:
    tmState = 'working'

  parallel for rm in rmState.keys():
    serial:  
      vote = ""
      atomic: 
        vote = RmPrepare(rm)

      if vote == 'prepared':
        tmPrepared.add(rm)
      elif vote == 'aborted':
        atomic: 
          TmAbort()
        return

  if len(tmPrepared) == len(rmState):
    atomic:
      TMCommit()


func TmAbort():
  tmState = 'aborted'
  parallel for rm in rmState.keys():
    atomic:
      RmAbort(rm)

func TMCommit():
  tmState = 'committed'
  parallel for rm in rmState.keys():
    atomic:
      RmCommit(rm)

func RmPrepare(rm):
  oneof:
    rmState[rm] = 'prepared'
    rmState[rm] = 'aborted'

  return rmState[rm]

func RmAbort(rm):
    rmState[rm] = 'aborted'

func RmCommit(rm):
    rmState[rm] = 'committed'

{{% /fizzbee %}}

When you run the code, you will see a deadlock error. But it still passed the
safety invariant, and generated around 100 states.
Open the state graph, you can see various cases. But everything is caused
by a crash, and our system is not modelling it.
When a single transaction crash happens, the client would
timeout and do something with that, but we are not modelling that.

## Deadlock
The reasons for the deadlock in this implementation are,
1. We model a single transaction. If it crashes, we don't cleanup anything.
   - In real implementation, the client will error out or timeout and do something.
2. Even after successful commit/abort, we do not have a future transactions, 
   as we have only a single transaction.

Although we could model that, but for now, we will just skip that.
Just add this, do nothing action to avoid the deadlock.

```python
action NoOp:
  pass
```
The TLA+ implementation and functional style FizzBee implementation avoided deadlock
because once committed or aborted a transaction, they continued to allow writing committed or aborted.

For example:
```python
atomic action RMRcvCommitMsg:
  any rm in rmState:
    if ('Commit') in msgs:
        rmState[rm] = 'committed'
```
If it added a check to see if rmState[rm] is not alreadu committed,
it would have also deadlocked.

## Complete code
{{% fizzbee %}}
always assertion ResMgrsConsistent:
  for rm1 in rmState.keys():
    for rm2 in rmState.keys():
      if rmState[rm1] == 'committed' and rmState[rm2] == 'aborted':
        return False
  return True

action Init:
  tmState = 'init'
  rmState = {1: 'init', 2:'init'}
  tmPrepared = set([])

action TmWrite:
  if tmState != 'init':
      return
  else:
    tmState = 'working'

  parallel for rm in rmState.keys():
    serial:  
      vote = ""
      atomic: 
        vote = RmPrepare(rm)

      if vote == 'prepared':
        tmPrepared.add(rm)
      elif vote == 'aborted':
        atomic: 
          TmAbort()
        return

  if len(tmPrepared) == len(rmState):
    atomic:
      TMCommit()


func TmAbort():
  tmState = 'aborted'
  parallel for rm in rmState.keys():
    atomic:
      RmAbort(rm)

func TMCommit():
  tmState = 'committed'
  parallel for rm in rmState.keys():
    atomic:
      RmCommit(rm)

func RmPrepare(rm):
  oneof:
    rmState[rm] = 'prepared'
    rmState[rm] = 'aborted'

  return rmState[rm]

func RmAbort(rm):
    rmState[rm] = 'aborted'

func RmCommit(rm):
    rmState[rm] = 'committed'

atomic action NoOp:
  pass

{{% /fizzbee %}}

## Compare with other formal methods

I couldn't find a pure PlusCal implementation, but a slightly modified version
https://github.com/muratdem/PlusCal-examples/blob/master/2PCTM/2PCwithBTM.tla


Note: This article shows the Procedural style of implementation.

FizzBee is a multi-paradigm language, so you can use the style that suits you best.

- [Two phase commit - functional style](/examples/two_phase_commit/)
- [Two phase commit - actors style](/examples/two_phase_commit_actors/)
