---
title: Automated Fault Injection
weight: 15
---

FizzBee is designed specifically for software engineers and architects working on distributed systems.
Therefore, FizzBee supports some unique features that are not common in typical formal methods tools like TLA+.

One such feature is that FizzBee model checker handles fault injection automatically. 
We will see how to use the implicit fault injection in FizzBee. 

{{< toc >}}

## Use non-atomic actions

Unlike TLA+ where every action is atomic, FizzBee allows you to define actions as atomic or non-atomic.
When every action is modelled as atomic, 
- you will be responsible to model various failure scenarios explicitly.
- you will need to explicitly model sequential operations.

In TLA+, an action defines a single state transition. That means, each action must be atomic and isolated.

Whereas, in FizzBee, an action is just like any other function call, but the caller of that function
is not modelled explicitly. For example, an action in FizzBee could be something invoked by
an user action, or a timer, or a network message or any other thing. Here, we don't care
how the action is triggered, but just say that could be triggered.
So, an action could involve a sequence of operations, and that means multiple state transitions.

When there are multiple state transitions in an action, there could be a failure in between.
So, fizzbee injects various types of faults automatically. But the only way to leverage is to
model the actions as non-atomic.

## Faults injected

These are the list of faults that are injected implicitly by FizzBee.

1. Message loss
2. Network partition
3. Thread crash
4. Node/process crash (Loss of ephemeral state)
5. Disk failure (Loss of persistent state)

Some faults not injected, but needs explicit modelling are
1. Byzantine faults
2. Message duplication
3. Disk corruption
4. Memory corruption


### Message loss
Since most distributed systems are built on top of unreliable networks, message loss is a common fault.
When a message is lost, the system might not make progress, or might make incorrect progress.
Like most practical systems, the network message delivery is at most once by default. To use
at least once you would need to model explicit retries.

Let us see a simple message passing example over unreliable network.

{{% fizzbee %}}
---
deadlock_detection: false
options:
    max_actions: 1
    max_concurrent_actions: 1
---

role Sender:
  action Init:
    self.state = 'init'

  action Send:
    self.state = 'calling'
    res = r.Process()
    self.state = 'done'

role Receiver:
  func Process():
    self.state = 'done'

action Init:
  r = Receiver()
  s = Sender()

{{% /fizzbee %}}

When you run this example, and open the state transition graph, you will see that
after a Send action is triggered, the system can reach one of the 3 states.

1. Sender in 'calling' state. But the receiver did not receive. Although, the graph just says 'crash',
   it implies any of these scenario.
   - Application called the rpc code, but the sending thread crashed before sending
   - Application sent, but the network dropped the message and call timeout
   - Application sent, the receiver received but the receiver thread crashed before it could process

2. Sender in 'calling' state. Receiver in 'done' state. This is the scenario where the message was delivered, 
   but the response was lost. Similar to the previous case, the `crash` could imply
   either the message lost or the receiver's thread crashed just before sending the response msg or
   the sender received the response but the thread crashed before the message could be processed.

3. Sender in 'done' state. Receiver in 'done' state. This is the normal scenario where the message was delivered.

Let us add some assertion. If a message is sent, the sender must eventually reach the 'done' state.

```python

always eventually assertion Done:
    return s.state == "init" or s.state == "done"

```

The liveness property `Done` will fail because of the message loss.

Let us make a small change in the yaml config at the top.
```yaml
deadlock_detection: false
options:
    max_actions: 100
    max_concurrent_actions: 1
```
and make the `Send` action `fair`.

This will allow Send to be called infinitely, and the liveness property will eventually pass.

While it is technically possible for the messages to be lost continuously it is highly unlikely
and gives uninteresting scenario, so FizzBee ensures the fault behavior is practical.


### Network partition
Network partition is just a special case of message loss, where all messages
between two sets of nodes are lost for an extended period of time.
Since FizzBee explores all possible transitions - including all possible 
message loss configurations, it will automatically explore the network partition scenarios.

### Thread crash
When an action is being processed, it is possible for the thread to crash at an 
arbitrary yield point.
When a thread crashes, if the action had a sequence of steps, the later steps will not get executed.

Let us see a simple example of thread crash. We will have a single Send action,
once triggered there is an infinite loop that will retry forever.

{{% fizzbee %}}
---
deadlock_detection: false
options:
    max_actions: 1
    max_concurrent_actions: 1
---

role Sender:
  action Init:
    self.state = 'init'

  fair action Send:
    self.state = 'calling'
    while True:
        res = r.Process()
    self.state = 'done'

role Receiver:
  func Process():
    self.state = 'done'

action Init:
  r = Receiver()
  s = Sender()

always eventually assertion Done:
    return s.state == "init" or s.state == "done"

{{% /fizzbee %}}

When you run this example, you will see that the `Send` crash at some point, and so,
the infinite loop will be exited due to the crash.

### Node/process crash (Loss of ephemeral state)
Node or process crash is a special case of thread crash, where all the threads are killed.
This is model checked by default without requiring any additional specification

But when a process crashes, all the ephemeral state is lost. At present, all the state variables
of a role are considered `durable` by default. So, when a process crashes, all the state variables are retained.

To the same example, we will add two counters `Sender.request_sent` and `Receiver.request_received`.

{{% fizzbee %}}
---
deadlock_detection: false
options:
    max_actions: 1
    max_concurrent_actions: 1
---

role Sender:
  action Init:
    self.state = 'init'
    self.request_sent = 0

  action Send:
    atomic:
        self.state = 'calling'
        self.request_sent += 1
    res = r.Process()
    self.state = 'done'

role Receiver:

  action Init:
    self.state = "init"
    self.request_received = 0

  func Process():
    self.request_received += 1
    self.state = 'done'

action Init:
  r = Receiver()
  s = Sender()

always assertion RequestSentCountGteReceivedCount:
    return s.request_sent >= r.request_received

{{% /fizzbee %}}

In the normal operation, the `Sender.request_sent` will be always greater than or equal to `Receiver.request_received`.

If the counter's are not durable, then the assertion will fail when the sender crashes, because the `request_sent` will be lost.
To mark some states as `ephemeral` or `durable` you can use the `state` annotation to the role.

```python
@state(ephemeral=["request_sent"])
role Sender:
    # actions and functions
    pass
```
In this case, only the request_sent will be reset when the sender process crashes. The `Sender.state` variable
is still durable. If many variables are ephemeral, you can instead just mark only the durable variables.

```python
@state(durable=["state"])
role Sender:
    # actions and functions
    pass
```

Now try this example in the playground, and you will see that the assertion will fail when the sender crashes.
{{% fizzbee %}}
---
deadlock_detection: false
options:
    max_actions: 1
    max_concurrent_actions: 1
---

@state(ephemeral=["request_sent"])
role Sender:
  action Init:
    self.state = 'init'
    self.request_sent = 0

  action Send:
    atomic:
        self.state = 'calling'
        self.request_sent += 1
    res = r.Process()
    self.state = 'done'

role Receiver:

  action Init:
    self.state = "init"
    self.request_received = 0

  func Process():
    self.request_received += 1
    self.state = 'done'

action Init:
  r = Receiver()
  s = Sender()

always assertion RequestSentCountGteReceivedCount:
    return s.request_sent >= r.request_received
{{% /fizzbee %}}

When you run, it will show the invariant failure when the sender crashes.

### Disk failure (Loss of persistent state)
This is a work in progress where will make the node becomes permanently unavailable.
That would implicitly imply the loss of persistent state. Since this is not
typically modelled in many distributed systems, this must be explicitly enabled
with a configuration.

For liveness properties will need to be adjusted to take into account the loss of nodes.
For example, instead of saying `all the receivers must eventually agree`, we might say
`all the receivers that are alive must eventually agree`.







