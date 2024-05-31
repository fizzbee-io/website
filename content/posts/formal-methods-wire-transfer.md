---
title: 'Introducing FizzBee: Simplifying Formal Methods for All'
type: posts
date: 2024-05-31
tags:
  - formal methods
  - system design
  - architecture
  - example
  - beginner
---


Building a complex distributed system? How do you verify your design doesn't have issues with consistency, performance or fault tolerance?

Amazon has been using formal methods to verify its distributed systems since 2012. Now, major players like Amazon, Microsoft, MongoDB, Confluent, Oracle, Elastic, CockroachDB, and many more are all embracing formal methods for their systems. Despite the immense benefits and relevance of this technique in modern software development, its widespread adoption has been hindered by the complexity of existing tools.

In this article, we’ll introduce you to [FizzBee](https://fizzbee.io), a new formal methods system that you can grasp in just a weekend.

## What Are Formal Methods?

Formal methods encompass rigorous techniques employed to specify, model, design, and verify complex systems using mathematical logic. Particularly relevant to software engineers working on cloud-based SaaS or distributed systems, concurrent programming, and similar domains, these methods offer a systematic approach to guarantee correctness and reliability in both software and hardware systems.

> Formal methods find bugs in system designs that cannot be found through any other technique we know of.
— Chris Newcombe, AWS

## How Do We Find System Design Bugs Today?
Today, we rely on drafting design documents and team reviews to uncover system design bugs. However, this approach falls short due to its inefficiency and limited effectiveness. We rely on pattern matching based on past experiences and known anti-patterns to identify design flaws because we lack the mental capacity and time to explore every possible outcome. This is where computers excel: effortlessly exploring billions of states in minutes.

## FizzBee: Formal Methods for All

FizzBee, a recent addition to formal methods systems, closes the accessibility gap with its user-friendly interface and Python-like syntax. This makes it easy for developers of all levels to express complex algorithms and system designs.

1. **Easy to learn**: If you’ve written a few Python scripts, you can grasp FizzBee code in just 10 minutes. Then, you can learn model-checking principles in a few hours.
1. **Enhanced Readability**: FizzBee specifications are designed for easy comprehension by both reviewers and developers. Unlike other tools like TLA+, FizzBee’s familiar syntax ensures that even non-authors can understand the specifications, facilitating smoother review processes and implementation.
1. **Multi-Paradigm Flexibility**: FizzBee offers versatile programming options, including functional, imperative, structured, procedural, and object-oriented styles. This allows developers to choose the best approach for each problem, leading to concise and adaptable solutions.
1. **Visualization**: FizzBee’s state transition graph aids in debugging by providing a visual representation. This also improves understanding of the model-checking process and helps users identify and resolve issues more effectively.
1. **Online Playground**: FizzBee provides an online playground for practicing, experimenting, and exploring examples, making it accessible for both learning and exploration.

## Modeling a Wire Transfer System
Let’s model a simple money transfer between two accounts, a classic example showcasing database transaction consistency. The aim is to ensure that no money is lost or gained unexpectedly, maintaining the total amount across all users in the system at the end of the day.

### First Implementation
Let’s keep it simple, we have two users: Alice and Bob. Only Alice is permitted to initiate wire transfers to Bob.

```
action Init:
    balances = {'Alice': 3, 'Bob': 2}

action FundTransfer:
    any amount in range(0,100):
        if balances['Alice'] &gt;= amount:
            balances['Alice'] -= amount
            balances['Bob'] += amount
```

#### Actions:

*Actions* are building blocks of the system’s behavior specification, representing various behaviors, operations, or events like user interactions or timer events. The model checker calls these actions repeatedly in different sequences to explore the system’s potential states.

In our model, we define two actions using the `action` keyword. The first is `Init`, a special action called first and only once. The second action is `FundTransfer`, which is the sole action in our model and called repeatedly.

#### State:

The variables defined in the `Init` action become the system’s state variables, which later actions can modify. In our example, a single state variable is represented by a Python dictionary containing two accounts with balances of 3 and 2.

#### Non-determinism:

When testing an implementation, we often test with a single value. However, with FizzBee, you specify the possible values, and the model checker explores all combinations.

In this example, you select an amount to transfer from the range 0 to 100. `any` is one of two keywords used to specify non-determinism. Syntactically, this is equivalent to a Python `for` statement, allowing you to rerun the same test with different amounts.

The remaining code is straightforward: if Alice has the funds to transfer, the amount is deducted from her account and added to Bob’s.

#### Invariants:

In system modeling, it’s crucial to ensure certain properties hold true. One essential property is that the sum of balances in all accounts must equal 5.

There are three types of invariants: *safety* (conditions that must always be true), *liveness* (conditions that must eventually become true), and *stability* (conditions that must eventually become true and remain true).

Let’s start with an assertion that balances should always match, similar to transfers between accounts in the same bank.

Invariants are specified using the `assertion` keyword.

```
always assertion BalanceMatchTotal:
    total = 0
    for balance in balances.values():
        total += balance
    return total == 5
```

An `assertion` is akin to a Python function but expects a `Boolean` return value. `True` implies the condition is true in that state.

The `always` keyword implies that this condition must hold true in every state.

### Run the model checker.

The model checker will indicate a failure, showing a trace where a context switch occurs after deducting from Alice’s account but before crediting Bob’s account.

![Transfer without transaction failed](https://dev-to-uploads.s3.amazonaws.com/uploads/articles/3f0l2q7zi06ptbjtk859.png)

Fix: Put these two steps in a transaction.

#### atomic keyword:

Using `atomic` ensures that both intermediate steps happen together or not at all, shielding them from the rest of the system. During development, this translates to a transaction or lock. By default, the behavior is serial, but you can explicitly specify otherwise.
```
atomic action FundTransfer:
    any amount in range(0,100):
        if balances['Alice'] >= amount:
            balances['Alice'] -= amount
            balances['Bob'] += amount
```

After applying `atomic`, running the model checker succeeds. You can also review the full state graph to observe the system’s behavior.

![Fund transfer in a transaction](https://dev-to-uploads.s3.amazonaws.com/uploads/articles/jwe7nmmby3m7s7je66h1.png)

#### Wire transfer — non atomic money transfer

Let us change the requirement to say once a wire transfer request is received, Alice’s account will be deducted immediately, but Bob’s account may not be credited immediately. We just want to ensure it will be credited eventually.

Let us start with the assertion. Instead of saying always, change from `always` to `always eventually`. From any state it will *eventually* reach a state where the predicates become true. This is called liveness expectation. (The stability expectation is specified with eventually always, this is less used and not covered here).
```
always eventually assertion BalanceMatchTotal:
    total = 0
    for balance in balances.values():
        total += balance
    return total == 5
```

Now, as a first attempt, remove the atomic keyword (or replace it with the serial keyword). So, the debiting and crediting happens in two separate steps

Now, when you run the command, you will see it failed with this trace.

![Liveness failed with stutter](https://dev-to-uploads.s3.amazonaws.com/uploads/articles/2fwj1p131fucpmrbhuv5.png)

This indicates, after deducting, the system could crash and if it did, it loses the next steps and stutter Stutter indicates, the system may not make any more progress.

Actions indicate what may happen in the system, not what must happen. We need to specify what must happen. This is done by adding keyword `fair` to an action.

Note: in this case, if we mark the FundTransfer action as fair, it just implies Alice would be able to keep sending the money, but it will be possible, the money will never reach Bob.

### Implementing wire transfer

It happens in two actions. In the first action, atomically, record the wire request and deduct from Alice’s account. On a second action, again atomically mark the transfer as complete and credit Bob’s account.

```
always eventually assertion BalanceMatchTotal:
  total = 0
  for balance in balances.values():
    total += balance
  return total == 5

action Init:
  balances = {‘Alice’: 3, ‘Bob’: 2}
  wire_requests = []

atomic action Wire:
  any amount in range(1,10):
    if balances[‘Alice’] >= amount:
      balances[‘Alice’] -= amount
      wire_requests.append((‘Alice’, ‘Bob’, amount))

atomic fair action DepositWireTransfer:
  any req in wire_requests:
    balances[req[1]] += req[2]
    wire_requests.remove(req)
```

Here, we are keeping a list of wire requests indicating the pending requests for wire transfers that need to be completed. And the Action DepositWireTransfer completes the step by crediting Alice’s account.

Run this model, you will notice an error — Deadlock.

![Deadlock due to single transaction](https://dev-to-uploads.s3.amazonaws.com/uploads/articles/h1f320rfprqa226od9fi.png)

That is because, as the system starts transferring funds from Alice to Bob, Alice runs out of money and the system cannot make any progress. This is an issue with our problem statement, rather than the model or implementation. We can easily fix it by allowing Bob to transfer money back to Alice. We will make that change later. For now, to keep things simple, let us do a tiny trick — add an action that does nothing. Real code would never need this.

```
# Add this temporarily until we fix Bob to transfer money to Alice
atomic action NoOp:
  pass
```

Now run this model checker, you will notice the model checker passes. This implies this design is correct.

Note: The model will not be directly transferable to code because wire_requests cannot be implemented in the current form. Is it a database in the same bank as the sender? Then, the receiver’s bank will not be able to atomically update along with crediting the sender. We will address it in a later post.

You can read more about [FizzBee](https://fizzbee.io/tutorials) and try other examples(https://fizzbee.io/examples).

#### Formal Verification Is Testing Your Design Before Coding
Formal verification allows you to test your design before coding. As demonstrated above, it helps you concentrate on the essentials and abstract away the details, similar to explaining a design using a basic example on a whiteboard.

By using formal verification, you can make sure your design is clear and correct before you start coding. However, it’s essential to remember that while formal verification tests the design well, it doesn’t replace the need for regular testing. Bugs can still crop up during implementation, but they’re usually easier to fix.

## Final Thoughts:
Formal methods stand out as the premier choice for design validation. Practitioners consistently highlight significant design simplification and faster implementation. For instance, in a recent project where I redesigned a buggy v1 system, specifying the v2 system’s design with TLA+ led to a 4x reduction in code size while incorporating additional features. However, it’s important to note that tools like TLA+ are notoriously challenging to use.

As shown in the example above, FizzBee code is easy to read and write, unlike TLA+, making it a compelling alternative for experienced software engineers to start formal methods for the first time. With FizzBee’s model checker, design correctness is ensured, while its concise and clear specifications communicate and document the design.

Originally published at [The New Stack](https://thenewstack.io/introducing-fizzbee-simplifying-formal-methods-for-all/)
