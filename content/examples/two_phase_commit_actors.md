---
title: Two Phase Commit (Actor model/Object oriented)
weight: 11
---

{{< toc >}}

# Two Phase Commit (Object oriented/Actor style implementation)

This is another implementation style in FizzBee to model the Two Phase Commit protocol.
There are two other styles,
1. [Functional style](/examples/two_phase_commit/) similar to TLA+
2. [Procedural style](/examples/two_phase_commit_procedural/) similar to PlusCal
3. Object oriented style (this post) similar to P

The significant benefit of this style is, it would feel more natural to the actual implementation,
but at the same higher level of abstraction as the other styles but more concise than the other options.

For more information about Roles, refer to [Roles](/tutorials/roles/).

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
But here, they may represent a participant in a system. It could be a,
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

Unlike the P model checker that has separate send semantics and new method, to use the channels
there is no syntax change. Just call the other function like a normal function call.

As you saw in the previous example, message passing is just a function call. To make it even easier,
the default channels are defined that you would never need to deal with these in most
cases.

By default, 
- For intra role communication,
  * Blocking, exactly once, unordered
- For inter role communication,
  * Blocking, at most once, unordered


## Implementation

### Roles - Participants

In the procedural approach, we had 3 state variables, `tmState`, `rmState`, `tmPrepared`.
As the names indicate, `rmState` corresponds to the states of each participant.
It's key and value, will become the state variables for each participant.

Similarly, RmPrepare, RmAbort and RmCommit will become the functions for each participant.

At this point, the syntax should be familiar.

```python

role Participant:
  action Init:
    self.state = "working"

  fair action Timeout:
    if self.state == "working":
      self.state = "aborted"

  func Prepare():
    if self.state != 'working':
      return self.state
    oneof:
      self.state = 'prepared'
      self.state = 'aborted'
    return self.state

  func Commit():
    self.state = 'committed'

  func Abort():
    self.state = 'aborted'

  action Terminated:
    if self.state == 'committed':
      pass

```

### Role - Coordinator
Coordinator has `state` and list of prepared participants.


```python

role Coordinator:

  action Init:
    self.prepared = set()
    self.state = "init"

  action Write:
    if self.state != "init":
      return
    self.state = "working"
    for rm in self.PARTICIPANTS:
      vote = rm.Prepare()

      if vote == 'aborted':
        self.Abort()
        return

      self.prepared.add(rm.ID)
    
    self.Commit()


  fair action Timeout:
    if self.state != "committed":
      self.Abort()

  fair action Restart:
    if self.state == "committed":
      for rm in self.PARTICIPANTS:
        rm.Commit()

  func Abort():
      self.state = "aborted"
      for rm in self.PARTICIPANTS:
          rm.Abort()

  func Commit():
    if self.state == 'working' and len(self.prepared) == len(self.PARTICIPANTS):
      self.state = 'committed'
      for rm in self.PARTICIPANTS:
        rm.Commit()
```

### Driver program 
Now, we just need a way to instantiate the roles and connect them.

```python

action Init:
  participants = []
  for i in range(NUM_PARTICIPANTS):
    p = Participant(ID=i)
    participants.append(p)

  coordinator = Coordinator(PARTICIPANTS=participants)

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

### Liveness invariant
```python
eventually always assertion Terminated:
  return coordinator.state in ('committed', 'aborted')
```

## Complete code

{{% fizzbee %}}

NUM_PARTICIPANTS = 2

role Coordinator:

  action Init:
    self.prepared = set()
    self.state = "init"

  action Write:
    if self.state != "init":
      return
    self.state = "working"
    for rm in self.PARTICIPANTS:
      vote = rm.Prepare()

      if vote == 'aborted':
        self.Abort()
        return

      self.prepared.add(rm.ID)
    
    self.Commit()


  fair action Timeout:
    if self.state != "committed":
      self.Abort()

  fair action Restart:
    if self.state == "committed":
      for rm in self.PARTICIPANTS:
        rm.Commit()

  func Abort():
      self.state = "aborted"
      for rm in self.PARTICIPANTS:
          rm.Abort()

  func Commit():
    if self.state == 'working' and len(self.prepared) == len(self.PARTICIPANTS):
      self.state = 'committed'
      for rm in self.PARTICIPANTS:
        rm.Commit()


role Participant:
  action Init:
    self.state = "working"

  fair action Timeout:
    if self.state == "working":
      self.state = "aborted"

  func Prepare():
    if self.state != 'working':
      return self.state
    oneof:
      self.state = 'prepared'
      self.state = 'aborted'
    return self.state

  func Commit():
    self.state = 'committed'

  func Abort():
    self.state = 'aborted'

always assertion ResMgrsConsistent:
  for rm1 in participants:
    for rm2 in participants:
      if rm1.state == 'committed' and rm2.state == 'aborted':
        return False
  return True

eventually always assertion Terminated:
  return coordinator.state in ('committed', 'aborted')


action Init:
  participants = []
  for i in range(NUM_PARTICIPANTS):
    p = Participant(ID=i)
    participants.append(p)

  coordinator = Coordinator(PARTICIPANTS=participants)
{{% /fizzbee %}}

## Diagrams
### Communication Diagram
Click on the `Communication Diagram` link to see the communication diagram.
This shows the various roles and the messages exchanged between them.

{{% graphviz %}}
digraph G {
  node [shape=box];
  splines=false;
  rankdir=LR;
  "Participant" [shape=none label=<<table cellpadding="14" cellspacing="8" style="dashed">
      <tr><td port="p0">Participant#0</td></tr>
      <tr><td port="p1" border="0">&#x022EE;</td></tr>
      <tr><td port="p2">Participant#2</td></tr>
      </table>>]
  "Coordinator" -> "Participant":p0 [label="Prepare, Abort, Commit"];
  "Coordinator" -> "Participant":p2 [label="Prepare, Abort, Commit"];
  "FairActionParticipant" [shape=none label=<<table cellpadding="14" cellspacing="8" style="invisible"><tr>
      <td port="Timeout"></td>
      </tr></table>>]
  { rank=same; "Participant"; "FairActionParticipant"; }
  "FairActionParticipant":Timeout -> "Participant" [label="Timeout"];
  "actionCoordinatorWrite" [label="" shape="none"]
  "actionCoordinatorWrite" -> "Coordinator" [label="Write"];
  "FairActionCoordinator" [shape=none label=<<table cellpadding="14" cellspacing="8" style="invisible"><tr>
      <td port="Timeout"></td>
      <td port="Restart"></td>
      </tr></table>>]
  { rank=same; "Coordinator"; "FairActionCoordinator"; }
  "FairActionCoordinator":Timeout -> "Coordinator" [label="Timeout"];
  "FairActionCoordinator":Restart -> "Coordinator" [label="Restart"];
}

{{% /graphviz %}}

### Interactive Sequence Diagram
This is a more detailed diagram. To generate this, first enable whiteboard and then run.
You will see `Explorer` link, click to open it.

On the left, play with the buttons to generate the sequence diagram.

  {{< mermaid class="text-center" >}}
sequenceDiagram
	note left of 'Coordinator#0': Write
	'Coordinator#0' ->> 'Participant#0': Prepare()
	'Participant#0' -->> 'Coordinator#0': ("prepared")
	'Coordinator#0' ->> 'Participant#1': Prepare()
	'Participant#1' -->> 'Coordinator#0': ("prepared")
	'Coordinator#0' ->> 'Participant#0': Commit()
	'Participant#0' -->> 'Coordinator#0': .
	'Coordinator#0' ->> 'Participant#1': Commit()
	'Participant#1' -->> 'Coordinator#0': .
   {{< /mermaid >}}

### Whiteboard diagram


   {{% graphviz %}}
digraph G {
compound=true;
subgraph "cluster_Participant#0" {
style=dashed;
label="Participant#0";
"Participant#0_placeholder" [label="" shape=point width=0 height=0 style=invis];
"Participant#0.state" [label="state = committed" shape=ellipse];
}
subgraph "cluster_Participant#1" {
style=dashed;
label="Participant#1";
"Participant#1_placeholder" [label="" shape=point width=0 height=0 style=invis];
"Participant#1.state" [label="state = committed" shape=ellipse];
}
subgraph "cluster_Coordinator#0" {
style=dashed;
label="Coordinator#0";
"Coordinator#0_placeholder" [label="" shape=point width=0 height=0 style=invis];
subgraph "cluster_Coordinator#0.prepared" {
style=dashed;
label="prepared";
"Coordinator#0.prepared" [shape=plaintext, label=<<table border="0" cellborder="1" cellspacing="0" cellpadding="6"><tr>
<td port="before" sides="r"></td>
<td port="0">0</td>
<td port="1">1</td>
<td port="after" sides="l"></td>
</tr></table>>];
}

"Coordinator#0.state" [label="state = committed" shape=ellipse];
}
"coordinator" [label="coordinator = role Coordinator#0" shape=ellipse];
"coordinator" -> "Coordinator#0_placeholder" [lhead="cluster_Coordinator#0"];
subgraph "cluster_null.participants" {
style=dashed;
label="participants";
"participants" [shape=plaintext, label=<<table border="0" cellborder="1" cellspacing="0" cellpadding="6"><tr>
<td port="before" sides="b"></td></tr>
<tr><td port="0">role Participant#0</td></tr>
<tr><td port="1">role Participant#1</td></tr>
<tr><td port="after" sides="t"></td>
</tr></table>>];
}
"participants":0 -> "Participant#0_placeholder" [lhead="cluster_Participant#0"];
"participants":1 -> "Participant#1_placeholder" [lhead="cluster_Participant#1"];
}
   {{% /graphviz %}}

## Compare with P

Compare this with the P model checker code.

https://github.com/p-org/P/tree/master/Tutorial/2_TwoPhaseCommit/PSrc

If you notice, the FizzBee code is more concise and closer to pseudocode.
In addition to being concise, FizzBee does exhaustive model checking. Whereas, P does not.
It explores various paths heuristically. That means, P cannot verify the correctness of the system, but FizzBee can.

Note: This post shows the Actor/Object oriented style of implementation.

FizzBee is a multi-paradigm language, so you can use the style that suits you best.

- [Two phase commit - functional style](/examples/two_phase_commit/)
- [Two phase commit - procedural style](/examples/two_phase_commit_procedural/)
