---
title: Two Phase Commit (Actor model/Object oriented)
weight: 11
---

# Two Phase Commit (Object oriented/Actor style implementation)

This is another implementation style in FizzBee to model the Two Phase Commit protocol.
There are two other styles,
1. [Functional style](/examples/two_phase_commit/) similar to TLA+
2. [Procedural style](/examples/two_phase_commit_procedural/) similar to PlusCal
3. Object oriented style (this post) similar to P

The significant benefit of this style is, it would feel more natural to the actual implementation,
but at the same higher level of abstraction as the other styles but more concise than the other options.

That said, it is work in progress, so not completely implemented yet.

For the details on the algorithm read through the previous posts.

One way to think of it is, this is just a syntactic sugar over the procedural styles.

## Quick overview
This document assumes, you are already familar with the procedural style.
Just go through the [Two Phase Commit (Procedural)](/examples/two_phase_commit_procedural/) doc to get a quick overview.

Two major new concepts used here are
1. Roles
2. Channels

### Roles
Roles are like classes in object oriented programming. They have states and actions.
But here, they may represent a participant in a system. It could be,
- microservice
- process
- thread
- just a role (Eg. coordinator, participant in 2-Phase Commit)
- database

If you are writing a design doc, and created a block diagram with it,
they most likely represent a role in the system.

Roles can have state, actions, functions and even assertions like
a top level spec. So basically, roles just provide a way to organize the code.

```python
role Server1:
  action Init(args):
    # ...
    
  action OtherAction:
    # ...
```

### Channels

The communication mechanism to connect two roles. 
This simplifies modeling of message passing.

- Blocking/NonBlocking  - default=blocking
- Delivery (at most once, at least once, exactly once) - default = “atmost_once”
- Ordering (unordered, pairwise, ordered) - ordering = “unordered”

Unlike P model checker that has separate send semantics and new method, to use the channels
there is no syntax change. Just call the other function like a normal function call.

As you saw in the previous example, message passing is just a function call. To make it even easier,
the default channels are defined that you would never need to deal with these in most
cases.

By default, 
- For intra role communication,
  * Blocking, exactly once, unordered
- For inter role communication,
  * Blocking, at least once, unordered


## Implementation

### Roles - Participants

In the procedural approach, we had 3 state variables, `tmState`, `rmState`, `tmPrepared`.
As the names indicate, `rmState` corresponds to the states of each participants.
It's key and value, will become the state variables for each participant.

Similarly, RmPrepare, RmAbort and RmCommit will become the functions for each participant.

At this point, the syntax should be familiar.

```python
role Participant:

  action Init(id):
    ID = id
    state = 'init'

  func Prepare():
    oneof:
      state = 'prepared'
      state = 'abort'
    return state

  func Abort():
      state = 'aborted'
  
  func Commit():
      state = 'committed'

```

### Role - Coordinator
`state` is the only state variable for the coordinator.
and needs references to all participants.

```python
role Coordinator:

  action Init(rms):
    state = 'init'
    participants = rms

  action Write:
    if state != 'init':
      return
    else:
      state = 'working'
  
    parallel for rm in participants:
      serial:
        prepared = set()
        vote = rm.Prepare()
  
        if vote == 'prepared':
          prepared.add(rm)
        elif vote == 'aborted':
          Abort()
          return
  
    if len(prepared) == len(participants):
      Commit()

  func Abort():
    state = 'aborted'
    parallel for rm in participants:
      rm.Abort()

  func Commit():
    state = 'committed'
    parallel for rm in participants:
      rm.Commit()

```

### Driver program 
Now, we just need a way to instantiate the roles and connect them.

```python

action Init:
  participants = [Participant(1), Participant(2), Participant(3)]
  coordinator = Coordinator(participants)

action NoOp:
  # To prevent deadlock errors as explained in the previous post
  pass

```

### Safety invariant
Although the invariants can be specified within the roles, it is easier
to verify the system level properties at the top level.
Especially, when the properties are not specific to a role like in the case
of two phase commit. We need a way to accesss the states of all participants.

In our case, we can put that in the global part itself.

```python
always assertion ResMgrsConsistent:
  for rm1 in participants:
    for rm2 in participants:
      if rm1.state == 'committed' and rm2.state == 'aborted':
        return False
  return True
```

## Complete code

{{% hint type = "caution" %}}
Roles are not supported in the playground yet. This will be added soon.
{{% /hint %}}

```python

role Participant:

  action Init(id):
    ID = id
    state = 'init'

  func Prepare():
    oneof:
      state = 'prepared'
      state = 'abort'
    return state

  func Abort():
      state = 'aborted'
  
  func Commit():
      state = 'committed'


role Coordinator:

  action Init(rms):
    state = 'init'
    participants = rms

  action Write:
    if state != 'init':
      return
    else:
      state = 'working'
  
    parallel for rm in participants:
      serial:
        prepared = set()
        vote = rm.Prepare()
  
        if vote == 'prepared':
          prepared.add(rm)
        elif vote == 'aborted':
          Abort()
          return
  
    if len(prepared) == len(participants):
      Commit()

  func Abort():
    state = 'aborted'
    parallel for rm in participants:
      rm.Abort()

  func Commit():
    state = 'committed'
    parallel for rm in participants:
      rm.Commit()

always assertion ResMgrsConsistent:
  for rm1 in participants:
    for rm2 in participants:
      if rm1.state == 'committed' and rm2.state == 'aborted':
        return False
  return True

action Init:
  participants = [Participant(1), Participant(2), Participant(3)]
  coordinator = Coordinator(participants)

action NoOp:
  # To prevent deadlock errors as explained in the previous post
  pass

```

## Compare with TLA+

In this spec, I tried to match the TLA+ style of modeling, where every action is atomic
following this example written by Leslie Lamport:
https://github.com/tlaplus/Examples/blob/master/specifications/transaction_commit/TwoPhase.tla

Feel free to notice the readability of the FizzBee spec vs the TLA+ spec.

If you are a TLA+ user, this style will be the quickest to get used to.
