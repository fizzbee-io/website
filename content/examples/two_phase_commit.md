---
title: Two Phase Commit
weight: 10
---

# Two Phase Commit

This is the classic distributed consensus algorithm - when you have
multiple databases participate in a transaction how to ensure
the transaction is committed atomically. That is, all databases
commit or none of them commit.

More details on this algorithm can be found in the wiki.
https://en.wikipedia.org/wiki/Two-phase_commit_protocol

In the post, we will model the Two Phase Commit protocol using FizzBee.

FizzBee is a multi-paradigm formal specification language and model checker.
Therefore, you can use functional style like TLA+, or imperative style like PlusCal
or even OOP style like Alloy.
{{< toc >}}

## Problem statement:
 
- There is one coordinator and multiple participants.
  * Note: The coordinator is just a role a server takes up for a single transaction
  * So the coordinator and one of the participants may be in the same machine.
- When a client issues a Write, the coordinator receives the request, and coordinates
  with all participants to commit or abort the transaction.
- Since there can be machine failures, it is not possible to ensure
  all participants either abort or commit. So, we will relax the requirement.
- Specifically,
  * if one participant committed, then no participants should abort.
  * if one participant aborted, then no participants should commit. (
    This is just rephrasing the above statement)
  * When one or more participants are committed [or aborted], the other
    participants can be in any state other than aborted [or committed] respectively.

{{% hint type=note %}}
It is impossible to guarantee termination in a consensus protocol with even
a single node failure. This is commonly known as FLP impossibility theorem.
See:
https://groups.csail.mit.edu/tds/papers/Lynch/jacm85.pdf

Therefore we will only prove safety, not liveness.
{{% /hint %}}

## Algorithm

The Two Phase Commit protocol has two phases:

1. Voting phase 
   1. The coordinator sends a `Prepare` message to all participants.
   2. Participants respond with `Prepared` or `Abort`.
2. Completion phase
   1. If all participants responded with `Prepared`, the coordinator sends `Commit` to all participants.
   2. If any participant responded with `Abort`, the coordinator sends `Abort` to all participants.
   3. Participants respond with `Ack` to the coordinator.

## How to model it with FizzBee

For modeling distributed algorithms, unlike the implementation, we can do it at a higher level
of abstraction. We do not even need to model the network, or the message passing.

Instead we can put it in a single shared variable that all participants can access.
Lamport has shown that we can model [distributed algorithms proving this accurately models
message passing](https://lamport.azurewebsites.net/pubs/lamport-theorem.pdf).



## Implementation

{{% hint type=note %}}
As noted before, in this implementation we will implement this similar to TLA+'s functional style
where every action is atomic.
We will include procedural style like PlusCal and object-oriented style like P in future examples.
{{% /hint %}}


### States

```python
action Init:
  # transaction manager state, starts in init state
  tmState = 'init'
  # 2 participants, starts in working state
  rmState = {1: 'working', 2:'working', 3:'working'}
  
  # set of participants that have responded with Prepared
  tmPrepared = set([])
  
  # set of all the messages in the system
  # Since we are specifying only safety, a process is not    *)
  # required to receive a message, so there is no need to model message *)
  # loss.  (There's no difference between a process not being able to   *)
  # receive a message because the message was lost and a process simply *)
  # ignoring the message.)
msgs = set([])
```

### Safety invariants

This must be obvious, the body of the assertion is Plain Old Python
that returns a boolean.

```python
always assertion ResMgrsConsistent:
  for rm1 in rmState:
    for rm2 in rmState:
      if rmState[rm1] == 'committed' and rmState[rm2] == 'aborted':
        return False
  return True
```


### Actions

#### Voting phase: Participant prepares to commit

```python
atomic action RMPrepare:
  any rm in rmState:
    if rmState[rm] == 'working':
      rmState[rm] = 'prepared'
      msgs.add(('Prepared', rm))
```
Try this part in the FizzBee model checker.

{{% fizzbee %}}
always assertion ResMgrsConsistent:
  for rm1 in rmState:
    for rm2 in rmState:
      if rmState[rm1] == 'committed' and rmState[rm2] == 'aborted':
        return False
  return True

action Init:
  tmState = 'init'
  rmState = {1: 'working', 2:'working', 3:'working'}
  tmPrepared = set([])
  msgs = set([])

atomic action RMPrepare:
  any rm in rmState:
    if rmState[rm] == 'working':
      rmState[rm] = 'prepared'
      msgs.add(('Prepared', rm))

{{% /fizzbee %}}

Run this in the playground, you can see the states including the choices it made to reach the state.
Ignore the deadlock error because we have not defined the other actions yet.

#### Voting phase: Participant chooses to abort
Any node that is in working state can choose to abort.
Participants need not explicitly send a message to the coordinator that they are aborting,
as it is always possible for the participants to terminate abruptly or
the network to fail in such a way that the coordinator does not receive the message.

```python
atomic action RMChooseToAbort:
  any rm in rmState:
    if rmState[rm] == 'working':
        rmState[rm] = 'aborted'
```

#### Voting phase: Coordinator receives Prepared msgs
Check the msgs set if a participant sent a prepared message.

```python
atomic action TMRcvPrepared:
  any rm in rmState:
    if tmState == 'init' and ('Prepared', rm) in msgs:
      tmPrepared.add(rm)
```
{{% hint type=note %}}
Remember, an action just says what can happen. It may never happen, or happen multiple times.
So, this already includes duplicate delivery and lost messages.
{{% /hint %}}


#### Completion phase: Coordinator aborts
The coordinator can choose to abort anytime, either because
of receiving the abort message from a participant or because of a timeout.
We can just ignore the cause, and say, the coordinator can choose to abort
as long as, it has not issued commit or abort message yet, that is in `init` state.

```python
atomic action TMAbort:
  if tmState == 'init':
    tmState = 'aborted'
    msgs.add(('Abort'))
```

#### Completion phase: Coordinator commits
If all the particiants are in the prepared set, the coordinator can commit.

```python
atomic action TMCommit:
  if tmState == 'init' and len(tmPrepared) == len(rmState):
    tmState = 'committed'
    msgs.add(('Commit'))
```

#### Completion phase: Participant receives commit msg

```python
atomic action RMRcvCommitMsg:
  any rm in rmState:
    if ('Commit') in msgs:
        rmState[rm] = 'committed'
```

#### Completion phase: Participant receives abort msg

```python
atomic action RMRcvAbortMsg:
  any rm in rmState:
    if ('Abort') in msgs:
        rmState[rm] = 'aborted'
```

## Full code

{{% fizzbee %}}

always assertion ResMgrsConsistent:
  for rm1 in rmState:
    for rm2 in rmState:
      if rmState[rm1] == 'committed' and rmState[rm2] == 'aborted':
        return False
  return True


action Init:
  tmState = 'init'
  rmState = {1: 'working', 2:'working', 3:'working'}
  tmPrepared = set([])
  msgs = set([])


atomic action TMRcvPrepared:
  any rm in rmState:
    if tmState == 'init' and ('Prepared', rm) in msgs:
      tmPrepared.add(rm)


atomic action TMCommit:
  if tmState == 'init' and len(tmPrepared) == len(rmState):
    tmState = 'committed'
    msgs.add(('Commit'))


atomic action TMAbort:
  if tmState == 'init':
    tmState = 'aborted'
    msgs.add(('Abort'))


atomic action RMPrepare:
  any rm in rmState:
    if rmState[rm] == 'working':
      rmState[rm] = 'prepared'
      msgs.add(('Prepared', rm))


atomic action RMChooseToAbort:
  any rm in rmState:
    if rmState[rm] == 'working':
        rmState[rm] = 'aborted'


atomic action RMRcvCommitMsg:
  any rm in rmState:
    if ('Commit') in msgs:
        rmState[rm] = 'committed'


atomic action RMRcvAbortMsg:
  any rm in rmState:
    if ('Abort') in msgs:
        rmState[rm] = 'aborted'

{{% /fizzbee %}}

## Compare with TLA+

In this spec, I tried to match the TLA+ style of modeling, where every action is atomic
following this example written by Leslie Lamport:
https://github.com/tlaplus/Examples/blob/master/specifications/transaction_commit/TwoPhase.tla

Feel free to notice the readability of the FizzBee spec vs the TLA+ spec, making FizzBee a viable
alternative to TLA+ and the easiest formal methods language so far.

If you are a TLA+ user, this style will be the quickest to get used to.

Remember, FizzBee is a multi-paradigm language, so you can use the style that suits you best.

- [Two phase commit - procedural style](/examples/two_phase_commit_procedural/)
- [Two phase commit - with Actors syle](/examples/two_phase_commit_actors/)
