---
title: Liveness and Fairness
description: Liveness ensures something good eventually happens. Learn how to model and verify liveness properties in FizzBee, from fairness levels to temporal logic—crucial for designing reliable distributed systems.
weight: -18
---

Safety ensures nothing bad happens, but liveness ensures something good _eventually_ does.
Liveness properties are the cornerstone of progress in distributed systems, 
guaranteeing that operations like message delivery, money transfers, and resource allocation eventually succeed.

{{% toc %}}

When designing a billing system, it's crucial to ensure users are not overcharged—that's safety. 
But it’s equally important to guarantee that users are eventually charged—that’s liveness. 

In distributed systems, liveness properties are often harder to prove than safety properties. We will
see how to model and verify liveness properties in FizzBee.

We briefly looked at liveness in the getting started guide, but let's dive deeper.

## Temporal Logic

This is the only section that will have some formal methods jargon. The rest of the guide is
more practical and hands-on.

In FizzBee we use temporal logic to specify liveness properties. Temporal logic extends propositional logic with operators to describe time and order of events.

{{% hint note %}}
There are formal approaches to model liveness properties besides temporal logic like
process algebra, automata theory and Fixed-Point Logic (µ-Calculus).

Temporal logic is the most popular and widely used in formal methods. 
Because it is expressive and easy to understand with limited mathematics background.
{{% /hint %}}

Temporal logic itself has two major variants:
- Linear Temporal Logic (LTL)
- Computation Tree Logic (CTL)
and derivatives of these like
- CTL* - a superset of CTL and LTL
- PCTL - Probabilistic Computation Tree Logic

FizzBee uses a subset of LTL to specify liveness properties. It also has
some limited support for CTL and probabilistic model checking. We will learn more about
these.

### Linear Temporal Logic (LTL)

TODO: Add some basic concepts

## Liveness Properties

To express liveness properties, we use the `eventually` keyword. But there are two kinds of liveliness properties:
- Eventually the system will reach a good state. This is specified  using `always eventually`
- Eventually the system will reach a good state and stay there forever. This property is
    called `stability`. Specified using `eventually always`

An example:

{{< fizzbee >}}
always eventually assertion SafelyShutdown:
  return status == "shutdown"

always eventually assertion Working:
  return status == "working"

action Init:
  status = "idle"

atomic fair<strong> action Start:
  if status == "idle":
    status = "working"

atomic fair action Finish:
  if status == "working":
    status = "idle"

atomic fair<strong> action Shutdown:
  if status not in ["working", "failed"]:
    status = "shutdown"

atomic action Fail:
  if status != "shutdown":
    status = "failed"

atomic fair action Fix:
  if status == "failed":
    status = "idle"
    
atomic fair action Restart:
  if status == "shutdown":
    status = "idle"
{{< /fizzbee >}}

Specifying liveness properties is easy. Just define the predicate as above, and
use the `always eventually` or `eventually always` keywords.

### CTL property: exists
At present, FizzBee does not support CTL properties. But it is in the roadmap.
But you can use the `exists` keyword to assert there is at least one state in one timeline
where this property holds. 

This is useful to assure that the state space covered some specific state.
Typically when modelling, we tend to temporarily add a safety assertion that will obviously fail.
This will give us the confidence the model checker is exploring the state space as intended.

And then we would remove those assertions before running the final model check.
Instead, you could use the `exists` keyword to assert that the state space covers the state.

Note: When this assertion fails, there won't be any counter example or stack trace. Because
the error is we can't find a state that satisfies the property. So, it is not a bug in the model checker.

Add this to the previous example:
{{< highlight python >}}

exists assertion HasFailedState:
  return status == "failed"

{{< /highlight >}}

You can test it by removing the Fail action. The assertion will fail.





## Fairness
Fairness is a crucial concept in liveness properties. When defining the model, we say what can happen to the system.

That is sufficient to define the safety properties. But to define liveness properties, we need to specify what must happen.

Fairness is a way to specify what must happen. It ensures that every enabled action eventually happens.

### Levels of fairness:

#### Unfair
This is the default. These actions may never happen. 
This is useful for actions that are not critical for the system correctness.

#### Weak Fairness
Weak fairness ensures that if an action is enabled infinitely (continuously enabled), it will happen infinitely often.
Weak fairness is typically used to
express actions that are usually triggered by an internal scheduler.
Since the scheduler is guaranteed to be invoked infinitely often, the action will be triggered.

Weak fairness is expressed with the `fair` keyword. We could also use `fair<weak>` to be explicit.


#### Strong Fairness
Strong fairness ensures that if an action is enabled infinitely often, and it will happen infinitely often in the future.
Unlike weak fairness that can be triggered anytime, to guarantee strong fairness
the developers must have some additional mechanism to ensure the action is triggered at the right time.

Weak fairness is expressed with `fair<strong>` keyword.

#### Eventual Fairness
This is a stronger form of fairness than strong fairness. Strong fairness is applicable for actions/operations,
but eventual fairness is applicable for each state. This is not part of the standard temporal logic and not supported
in other tools like TLA+. But it is a useful concept in practical distributed systems.
At present, FizzBee does not implement this in the standard model checker, but to use it FizzBee has
a special mode called `nondeterministic` model checker. At present, this does not work
with other types of fairness. It is in the roadmap that we would be able to 
use eventual fairness with other types of fairness.

We will see examples of when this will be needed in the later sections when discussing
nondeterministic model checker.

### Applicability

#### Action fairness
Fairness is typically specified at the action level. 

#### Choice (any or oneof) fairness
In some cases, we might want to specify fairness in choosing between the non-deterministic choices.
At present, it can only be specified with `any` keyword. Soon, oneof would also be supported.

This is useful to specify that when choosing between multiple elements, each one of the them would
be chosen fairly, and we would be choosing the same element infinitely.
For example: if you want to model repeatedly tossing a coin until a head occurs,
The system would progress only if the coin toss would eventually land a head.

{{% fizzbee %}}
action Init:
  values = [False, False]


atomic fair<strong> action Set:
    client = fair any range(len(values))
    values[client] = True
    

always eventually assertion AllTrue:
    return all(values)

{{% /fizzbee %}}


## Fairness scoped to Roles

For actions that are part of a role, the fairness is scoped to each role instance. This simplifies the fairness
specification and matches the practical distributed systems design.

For those familiar with TLA+, in TLA+ since there is no concept of roles, the fairness is scoped to the entire system.
So, to specify fairness for a specific role, it is a bit more complex. Whereas with FizzBee, it is simple.

## Example

An example where there are multiple servers that need to update state of multiple receivers.


{{% fizzbee %}}

NUM_SENDERS = 2
NUM_RECEIVERS = 2

role Sender:

    atomic fair<strong> action Send:
        id =  fair any range(len(receivers))
        r = receivers[id]
        r.Process(self.ID)

role Receiver:
    action Init:
        self.values = [False for i in range(NUM_SENDERS)]

    atomic func Process(id):
        self.values[id] = True
    
action Init:
  senders = []
  for i in range(NUM_SENDERS):
      senders.append(Sender(ID=i))
      
  receivers = []
  for i in range(NUM_RECEIVERS):
      receivers.append(Receiver())


always eventually assertion AllTrue:
    for r in receivers:
        if not all(r.values):
            return False
    return True

{{% /fizzbee %}}

Here, the `Send` action is fair and since it is part of the role, this ensures that each sender will eventually send a message.

To ensure each receiver will eventually receive a message from each sender, we need to specify `fair` to the `any` keyword
that chooses the receiver to send to.

## Non Deterministic Model Checker
The standard model checker is applicable if you have a deterministic system. Many distributed systems are non-deterministic.
And the correctness/liveness of the system relies on the non-determinism. In those cases, strong
fairness is not sufficient. 
Many distributed systems and algorithms are proven to be impossible to guarantee
liveness in a deterministic system. For example: the FLP impossibility result for consensus.
These inherently rely on non-determinism to guarantee liveness. 
Many derived features like leader elections, retries etc also rely on non-determinism like random delay/jitter.
Or randomly choosing an element to process.

FizzBee has a special mode called `nondeterministic` model checker. 

Example:
{{% fizzbee %}}
action Init:
  values = [False, False]


atomic fair<strong> action Set:
    client = fair any range(len(values))
    value = fair any [False, True]
    values[client] = value
    

always eventually assertion AllTrue:
    return all(values)

{{% /fizzbee %}}
When you run this system in the standard model checker, the liveness check will fail.

{{% graphviz %}}
digraph G {
  "0" [label="yield
Actions: 0, Forks: 0
State: {\"values\":\"[False, False]\"}
", color="black" penwidth="2" ];
  "1" [label="Set
Actions: 1, Forks: 1
State: {\"values\":\"[False, False]\"}
Threads: 0/1
", color="black" penwidth="1" ];
  "0" -> "1" [label="1: Set"];
  "2" [label="Any:client=0
Actions: 1, Forks: 2
State: {\"values\":\"[False, False]\"}
Threads: 0/1
", color="black" penwidth="1" ];
  "1" -> "2" [label="2: Any:client=0"];
  "2" -> "0" [label="3: Any:value=False"];
  "0" -> "1" [label="4: Set"];
  "5" [label="Any:client=1
Actions: 1, Forks: 2
State: {\"values\":\"[False, False]\"}
Threads: 0/1
", color="black" penwidth="1" ];
  "1" -> "5" [label="5: Any:client=1"];
  "5" -> "0" [label="6: Any:value=False"];
  "0" -> "1" [label="7: Set"];
  "1" -> "2" [label="8: Any:client=0"];
  "9" [label="yield
Actions: 1, Forks: 3
State: {\"values\":\"[True, False]\"}
", color="black" penwidth="2" ];
  "2" -> "9" [label="9: Any:value=True"];
  "10" [label="Set
Actions: 2, Forks: 4
State: {\"values\":\"[True, False]\"}
Threads: 0/1
", color="black" penwidth="1" ];
  "9" -> "10" [label="10: Set"];
  "11" [label="Any:client=0
Actions: 2, Forks: 5
State: {\"values\":\"[True, False]\"}
Threads: 0/1
", color="black" penwidth="1" ];
  "10" -> "11" [label="11: Any:client=0"];
  "11" -> "0" [label="12: Any:value=False"];
}

{{% /graphviz %}}

Attempt 2: 
This is not because of having 2 fair choices, but because of the non-determinism in choosing the value.
So, clever tricks like combining the choices into a single tuple using python like approaches also will not work.

{{% fizzbee %}}
action Init:
  values = [False, False]


atomic fair<strong> action Set:
    cv = fair any [ 
        (c,v) 
            for c in range(len(values))
            for v in [False, True]
    ]

    values[cv[0]] = cv[1]
    

always eventually assertion AllTrue:
    return all(values)

{{% /fizzbee %}}

That is, 
{{% graphviz %}}
digraph G {
  "0" [label="yield
Actions: 0, Forks: 0
State: {\"values\":\"[False, False]\"}
", color="black" penwidth="2" ];
  "1" [label="Set
Actions: 1, Forks: 1
State: {\"values\":\"[False, False]\"}
Threads: 0/1
", color="black" penwidth="1" ];
  "0" -> "1" [label="1: Set"];
  "1" -> "0" [label="2: Any:cv=(0, False)"];
  "0" -> "1" [label="3: Set"];
  "4" [label="yield
Actions: 1, Forks: 2
State: {\"values\":\"[True, False]\"}
", color="black" penwidth="2" ];
  "1" -> "4" [label="4: Any:cv=(0, True)"];
  "5" [label="Set
Actions: 2, Forks: 3
State: {\"values\":\"[True, False]\"}
Threads: 0/1
", color="black" penwidth="1" ];
  "4" -> "5" [label="5: Set"];
  "5" -> "0" [label="6: Any:cv=(0, False)"];
  "0" -> "1" [label="7: Set"];
  "8" [label="yield
Actions: 1, Forks: 2
State: {\"values\":\"[False, True]\"}
", color="black" penwidth="2" ];
  "1" -> "8" [label="8: Any:cv=(1, True)"];
  "9" [label="Set
Actions: 2, Forks: 3
State: {\"values\":\"[False, True]\"}
Threads: 0/1
", color="black" penwidth="1" ];
  "8" -> "9" [label="9: Set"];
  "9" -> "8" [label="10: Any:cv=(0, False)"];
  "8" -> "9" [label="11: Set"];
  "9" -> "0" [label="12: Any:cv=(1, False)"];
}

{{% /graphviz %}}

#### Using non-deterministic model checker

{{% hint %}}
Note: The non-deterministic here implies the system being modeled in non-deterministic.
FizzBee's model checker that is used to verify this behaviour is very much deterministic.
{{% /hint %}}

To use the non-deterministic model checker, add `liveness: nondeterministic` to the fizz.yaml config or the frontmatter.


{{% fizzbee %}}
---
liveness: nondeterministic
---

action Init:
  values = [False, False]


atomic fair<strong> action Set:
    client = fair any range(len(values))
    value = fair any [False, True]
    values[client] = value
    

always eventually assertion AllTrue:
    return all(values)

{{% /fizzbee %}}

## Another example

This is an example taken from the discussion from the [tlaplus google group](https://groups.google.com/g/tlaplus/c/YTV6_o7hqHs/m/EmENa_6tBQAJ)

> A number of actors each want to transition from IDLE to PREPARED, and then from PREPARED to DONE. Once an actor is DONE they stay DONE, but they can go backwards from PREPARED to IDLE if the situation looks dicey.
> 
> IDLE <---> PREPARED ---> DONE
> 
> The actors follow these rules:
> It is always safe to go from IDLE to PREPARED
> It is always safe to revert from PREPARED to IDLE
> It is only safe to go from PREPARED to DONE if every actor is PREPARED. Fortunately, the actors can atomically read each other's state and modify their own, so there's no "Two Generals" problem here.

This is a classic example of a distributed system where the liveness property is not guaranteed in a deterministic system.
The only way to guarantee liveness is to have non-determinism with the timing of the events.

{{% fizzbee %}}
# ---
# # liveness check will fail without the non-determinism
# liveness: nondeterministic
# ---

# Define atomic actions
action Init:
    AliceState = "IDLE"
    BobState = "IDLE"

atomic fair<strong> action AlicePrepare:
    if AliceState == "IDLE":
        AliceState = "PREPARED"

atomic action AliceRevert:
    if AliceState == "PREPARED":
        AliceState = "IDLE"

atomic fair<strong> action BobPrepare:
    if BobState == "IDLE":
        BobState = "PREPARED"

atomic action BobRevert:
    if BobState == "PREPARED":
        BobState = "IDLE"

atomic fair<strong> action AliceFinalize:
    if AliceState == "PREPARED" and BobState == "PREPARED":
        AliceState = "DONE"

always eventually assertion Finalized:
    return AliceState == "DONE"

{{% /fizzbee %}}

This will fail with the following error path:

{{% graphviz %}}
digraph G {
  "0" [label="yield
Actions: 0, Forks: 0
State: {\"AliceState\":\"\"IDLE\"\",\"BobState\":\"\"IDLE\"\"}
", color="black" penwidth="2" ];
  "1" [label="yield
Actions: 1, Forks: 1
State: {\"AliceState\":\"\"PREPARED\"\",\"BobState\":\"\"IDLE\"\"}
", color="black" penwidth="2" ];
  "0" -> "1" [label="1: AlicePrepare"];
  "1" -> "0" [label="2: AliceRevert"];
  "0" -> "1" [label="3: AlicePrepare"];
  "1" -> "0" [label="4: AliceRevert"];
  "5" [label="yield
Actions: 1, Forks: 1
State: {\"AliceState\":\"\"IDLE\"\",\"BobState\":\"\"PREPARED\"\"}
", color="black" penwidth="2" ];
  "0" -> "5" [label="5: BobPrepare"];
  "5" -> "0" [label="6: BobRevert"];
}

{{% /graphviz %}}

Now, try running this with the `liveness: nondeterministic` in the frontmatter or the fizz.yaml config.
(Just uncomment the frontmatter

