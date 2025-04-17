---
title: Modeling msg delivery guarantees
description: Learn how to model message delivery guarantees in distributed systems—ordered vs. unordered delivery, at most once, exactly once, at least once, message deduplication, and more.
weight: -10
aliases:
  - "/tutorials/msg-delivery-guarantees/"
---

When modeling distributed systems, the interprocess communication is usually
done through messages. Depending on the system used, there are multiple 
message delivery semantics and they need to be modeled correctly to ensure
the specification reflects the right assumption.

This post will show how to model different message delivery guarantees using basic
collections like set, list and bag(multiset). This technique should be familiar and 
applicable to any formal methods tool like TLA+ as well.

In a later post, we will see an even more powerful but concise way to model these
using FizzBee's channels.

{{< toc >}}

## Abstraction
If you have tried other formal methods tools, you might have heard of the
author talking about *thinking abstractly* and *above the level of code* and so on.
Message passing is usually where the authors would start mentioning these. 

Note: The abstraction in modeling is related but different from abstraction in programming,
and so many formal methods practitioners would argue that abstraction is hard when it is not.

The key idea of abstraction in formal modeling is, to think how you would describe the design
on a whiteboard to a colleague. You would not go into the details of how the message is sent,
but usually draw an arrow between two boxes and write the message content. Or,
if the messages have some persistence like Kafka or SQS, you would most likely draw a queue
as an array. That is exactly what you need to model.

In this post, let us see some examples of how to model different types of message delivery guarantees.
There are two major types of message delivery semantics.
- Ordering: Unordered, ordered or pairwise etc.
- Delivery: At most once, exactly once, or at least once
- Deduplication: Whether the system can handle duplicate messages (on publish) or not.


All the examples just use [basic collections like set, list and bag(multiset)](/tutorials/datastructures#collections).


## Unordered and exactly once
Store the messages in a set. The receiver selects any element, and drops the msg
in the same atomic step.

```python
action Init:
    msgs = genericset()

atomic action Send:
    msgs.add(record(score=5, message='Hello'))

atomic fair action Receive:
    any msg in msgs:
        process(msg)
        msgs.remove(msg)
        
atomic func process(msg):
    # Process the message
    pass
```


## Unordered and at most once
Just have an action to drop the message without processing.

```python
action Init:
    msgs = genericset()

atomic action Send:
    msgs.add(record(score=5, message='Hello'))

atomic action Drop:
    any msg in msgs:
        msgs.remove(msg)

atomic fair action Receive:
    any msg in msgs:
        process(msg)
        msgs.remove(msg)
        
atomic func process(msg):
    # Process the message
    pass
```

## Unordered and at least once
Don't remove the message after processing.


```python
action Init:
    msgs = genericset()

atomic action Send:
    msgs.add(record(score=5, message='Hello'))

atomic fair action Receive:
    any msg in msgs:
        process(msg)
        
atomic func process(msg):
    # Process the message
    pass
```


## Unordered, exactly-once without deduplication
If the sender sends the same message twice, the receiver will process it twice.

{{% hint %}}
Even if you internally use some kind of deduplication key, if it is not relevant to the modeling
you can ignore it here. If the key is relevant, you can use a map with the key as the index.

Just imagine, if you are explaining this design in a whiteboard, does the deduplication key matter?


{{% /hint %}}
```python
action Init:
    msgs = bag()

atomic action Send:
    msgs.add(record(score=5, message='Hello'))

atomic fair action Receive:
    any msg in msgs:
        process(msg)
        msgs.remove(msg)
        
atomic func process(msg):
    # Process the message
    pass
```

## Ordered and exactly once
Obviously if ordering is expected, just use a list, and maintain offset. Alternatively,
you can also remove the first element in the list. Do whichever communicates the design better.

For example: 
When using Kafka, the common pattern is to maintain an offset for each client.
But when using FIFO SQS, you would just remove the first element.

The reason is, with kafka, the clients are expected to maintain the offset but
with SQS, the system maintains and clears the messages delivered.

```python
action Init:
    sqs_fifo = []
    kafka_topic = []
    kafka_client_offset = -1

atomic action Send:
    sqs_fifo.append(record(score=5, message='Hello'))
    kafka_topic.append(record(score=5, message='Hello'))

atomic fair action ReceiveSQS:
    if sqs_fifo:
        process(sqs_fifo.pop(0))

atomic fair action ReceiveKafka:
    if kafka_client_offset < len(kafka_topic):
        kafka_client_offset += 1
        process(kafka_topic[kafka_client_offset])
```

## Ordered and at least once
Just don't increment the offset or remove the message after processing.

```python
action Init:
    sqs_fifo = []
    kafka_topic = []
    kafka_client_offset = -1

atomic action Send:
    sqs_fifo.append(record(score=5, message='Hello'))
    kafka_topic.append(record(score=5, message='Hello'))

atomic fair action ReceiveSQS:
    if sqs_fifo:
        process(sqs_fifo[0])
        oneof:
            sqs_fifo.pop(0)
            pass # Do nothing i.e, in this case, don't remove the message

atomic fair action ReceiveKafka:
    if kafka_client_offset < len(kafka_topic):
        process(kafka_topic[kafka_client_offset+1])
        oneof:
            kafka_client_offset += 1
            pass # Do nothing i.e, in this case, don't increment the offset
```

### Pairwise ordering
Maintain separate queues for each pair of sender and receiver.


## Summary
- Is order relevant? Use a list
- Is deduplication relevant? Use a set
- Is deduplication key relevant? Use a map
- Is at least once relevant? Don't remove the message after processing
- Is exactly once relevant? Remove the message after processing
- Is at most once relevant? Just drop the message without processing
