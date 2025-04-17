---
title: Channels
weight: 15
description: "Channels make modeling message passing as intuitive as sketching on a whiteboard. Learn how to define delivery, ordering, and blocking behavior with default and custom channels."

aliases:
  - "/tutorials/channels/"
---

Channels are the communication mechanism to connect two roles, and provides a concise
way to describe the system design close to how you would describe in a whiteboard.

This is an alternative to the approach we saw before using simple collections.
(Refer to [Modeling msg delivery guarantees](/tutorials/msg-delivery-guarantees/) for more details)

{{% hint warning %}}
This is work in progress. 

{{% /hint %}}



{{< toc >}}

### Channels

The communication mechanism to connect two roles. 
This simplifies modeling of message passing.

- Blocking/NonBlocking  - default=blocking
- Delivery (at most once, at least once, exactly once) - default = “atmost_once”
- Ordering (unordered, pairwise, ordered) - ordering = “unordered”

Unlike the P model checker that has separate send semantics and new method, to use the channels
there is no syntax change. Just call the other function like a normal function call.

Message passing is just a function call. To make it even easier,
by default, 
- When the caller's context is atomic, both the method call and the return msgs are assumed to be reliable.
- When the caller's context is non-atomic, it assumes RPC semantics. That is, the messages can be
  dropped after sending but before the receiver receives or 
  after the receiver returns but before the caller receives.

First we will see how the default channels work, then we will introduce custom channels.

### Default Channels
In this example, there are two roles - Sender and Receiver. Sender just calls
a function Process() on Receiver.

{{% fizzbee %}}
---
deadlock_detection: false
---

role Sender:
  action Init:
    self.state = 'init'

  action Send:
    if self.state != 'init':
        return
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

Note:
1. To simplify understanding, this spec limits to a single function call.
2. The yaml frontmatter at the top disables the deadlock detection. This is because, the
   receiver is in 'done' state, and the sender is in 'calling' state. This is a deadlock
   scenario, but it is intentional to show the different states.

If you are running on the local machine, you can remove those lines, and just
specify these as config in the yaml file.

Run the above spec in the FizzBee playground and look at the state graph.

Follow the graph, there will be 3 terminal states - from left to right.

1. Sender in 'calling' state. But the receiver did not receive. Although, the graph just says 'crash',
   it implies any of these scenario.
   - Application called the rpc code, but the process crashed before sending
   - Application sent, but the network dropped the message and call timeout
   - Application sent, the receiver received but the process crashed before it could process
2. Receiver in 'done' state. Sender in 'calling' state. Implies, the receiver processed,
   but failed before the sender application could process the response.
3. Sender and receiver in 'done' state. Implies, the call was successful.


### Custom Channels

```python
NonBlockingFifo = Channel(ordering='ordered', delivery='atleast_once', blocking='fire_and_forget')

role Sender:
  action Init:
    self.state = 'init'

  action Send:
    if self.state != 'init':
        return
    self.state = 'calling'
    r.Process()
    self.state = 'done'

role Receiver:
  func Process():
    self.state = 'done'

action Init:
  r = NonBlockingFifo(Receiver())
  s = Sender()

action NoOp:
  pass
```

When you run this spec, since the call is fireandforget, the sender will not wait for the receiver to
receiver or process the response. But it is guaranteed that the receiver will receive the message at least once.

That is, you'll see the following states in the graph.

1. (Terminal) Sender in 'done' and receiver in 'done'. Implies, the call was successful.
2. (Terminal) Receiver in 'done' but receiver in 'calling'.
3. (Transient) Sender in 'done' but receiver is not done. Eventually, the receiver will process,
   but temporarily, the sender can be done before the receiver processes because of `fireandforget`.

