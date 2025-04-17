---
title: Getting Started
description: Learn how to model systems with FizzBee. This guide walks you through writing your first FizzBee model, covering key concepts like actions, control flow, non-determinism, fairness, and correctness properties—no prior formal methods experience needed.
weight: -20
aliases:
  - "/tutorials/getting-started/"
---

This tutorial assumes you have a basic programming experience
and are familiar with Python programming language.
You don't need to be an expert in Python, but if you have written
some algorithms or scripts, you should be good to go.

{{< toc >}}

# Installation
[FizzBee](https://github.com/fizzbee-io/fizzbee) is an open-source project and is available on GitHub.
At present, there are no prebuilt binaries. You need to build the binary using Bazel.
The instructions are posted on the README.md file.

# Online Playground
A good way to get started is to use the [Online Playground](/play).
This tutorial will have links to the playground with prepopulated code.

# Writing your first FizzBee program

## HourClock Example
Let's model a simple clock that ticks every hour.

To follow the tutorial, all the embedded code will have
a link to the [Online Playground](/play) where the code is prepopulated.

Run the code, and try modifying the code to see how the model checker behaves.

{{% fizzbee %}}
action Init:
  hour = 1

atomic action Tick:
  if hour == 12:
    hour = 1
  else:
    hour += 1

{{% /fizzbee %}}

Click on the link above this code block, and click Run.

On the right side, you will see the output of the model checker.
And a link with 'States Graph' will show you the states the model reached.

{{% graphviz %}}
digraph G {
"0x1400012f500" [label="yield
Actions: 0, Forks: 0
State: {\"hour\":\"1\"}
", color="black" penwidth="2" ];
"0x1400012f500" -> "0x1400012f6e0" [label="Tick", color="black" penwidth="1" ];
"0x1400012f6e0" [label="yield
Actions: 1, Forks: 1
State: {\"hour\":\"2\"}
", color="black" penwidth="2" ];
"0x1400012f6e0" -> "0x1400012fa40" [label="Tick", color="black" penwidth="1" ];
"0x1400012fa40" [label="yield
Actions: 2, Forks: 2
State: {\"hour\":\"3\"}
", color="black" penwidth="2" ];
"0x1400012fa40" -> "0x1400012fc80" [label="Tick", color="black" penwidth="1" ];
"0x1400012fc80" [label="yield
Actions: 3, Forks: 3
State: {\"hour\":\"4\"}
", color="black" penwidth="2" ];
"0x1400012fc80" -> "0x1400012fec0" [label="Tick", color="black" penwidth="1" ];
"0x1400012fec0" [label="yield
Actions: 4, Forks: 4
State: {\"hour\":\"5\"}
", color="black" penwidth="2" ];
"0x1400012fec0" -> "0x1400020a180" [label="Tick", color="black" penwidth="1" ];
"0x1400020a180" [label="yield
Actions: 5, Forks: 5
State: {\"hour\":\"6\"}
", color="black" penwidth="2" ];
"0x1400020a180" -> "0x1400020a3c0" [label="Tick", color="black" penwidth="1" ];
"0x1400020a3c0" [label="yield
Actions: 6, Forks: 6
State: {\"hour\":\"7\"}
", color="black" penwidth="2" ];
"0x1400020a3c0" -> "0x1400020a600" [label="Tick", color="black" penwidth="1" ];
"0x1400020a600" [label="yield
Actions: 7, Forks: 7
State: {\"hour\":\"8\"}
", color="black" penwidth="2" ];
"0x1400020a600" -> "0x1400020a840" [label="Tick", color="black" penwidth="1" ];
"0x1400020a840" [label="yield
Actions: 8, Forks: 8
State: {\"hour\":\"9\"}
", color="black" penwidth="2" ];
"0x1400020a840" -> "0x1400020aa80" [label="Tick", color="black" penwidth="1" ];
"0x1400020aa80" [label="yield
Actions: 9, Forks: 9
State: {\"hour\":\"10\"}
", color="black" penwidth="2" ];
"0x1400020aa80" -> "0x1400020acc0" [label="Tick", color="black" penwidth="1" ];
"0x1400020acc0" [label="yield
Actions: 10, Forks: 10
State: {\"hour\":\"11\"}
", color="black" penwidth="2" ];
"0x1400020acc0" -> "0x1400020af00" [label="Tick", color="black" penwidth="1" ];
"0x1400020af00" [label="yield
Actions: 11, Forks: 11
State: {\"hour\":\"12\"}
", color="black" penwidth="2" ];
"0x1400020af00" -> "0x1400012f500" [label="Tick", color="black" penwidth="1" ];
}
{{% /graphviz %}}

As anyone familiar with Python would simplify this to,
{{% fizzbee %}}
action Init:
  hour = 1

atomic action Tick:
  hour = (hour % 12) + 1
{{% /fizzbee %}}

# Actions
Actions represent the 'actions' that can be taken in the system. These could be
something a user does, or a system event like a timer tick and so on.

In the above code, we have two actions `Init` and `Tick`.
Init is a special action that initializes the system. It is called only once.

`atomic` keyword is used to denote that the action is atomic. We will revisit this later.

Tick is our main action that increments the hour. If the hour is 12, it resets to 1.
An action indicates what can happen to the system.

# Syntax
The meat of the code is written in Starlark language that is a subset of Python.
So, the body of the action will be familiar to most programmers. Most of the constructs
like if-else, for and while loops are similar to Python.

Similarly, most common data structures like lists, dictionaries, tuples and sets are also similar to Python.

# Control Flow

## If-elif-else
Same as python: if-elif-else
```python
if a > b:
  b += 1
elif a < b:
  a += 1
else:
  a += 2
```
## While
Same as python: while. (Note: Python's else clause on while is not supported)
```python
while a < 5:
  a += 1
```
If a is 10 at the beginning, a will be 15 at the end.

## For
Same as python: for. (Note: Python's else clause on for is not supported)
Similar to `\A` in TLA+

{{% fizzbee %}}
action Init:
  value = 0
  for x in [1, 2, 3]:
    value += x

{{% /fizzbee %}}

When you run this code, you will see the value is 6 at the end of the Init action.

{{% graphviz %}}
digraph G {
  "0x14000121500" [label="yield
Actions: 0, Forks: 0
State: {\"value\":\"6\"}
", color="black" penwidth="2" ];
}
{{% /graphviz %}}

## Any 
The `any` keyword is similar in structure to the `for` loop. The only difference is that,
any indicates any one of the values in the list can be chosen. 

The model checker will then explore the possibilities of choosing each of these values.
Similar to `\E` in TLA+

{{% fizzbee %}}
action Init:
  value = 0
  any x in [1, 2, 3]:
    value += x

{{% /fizzbee %}}

Run this code in the playground, and compare the state graph with
using the for loop.

{{% graphviz %}}
digraph G {
  "0x1400002b560" [label="Init
Actions: 0, Forks: 0

Threads: 0/1
", color="black" penwidth="1" ];
  "0x1400002b560" -> "0x1400002bb00" [label="", color="forestgreen" penwidth="3" ];
  "0x1400002bb00" [label="yield
Actions: 0, Forks: 1
State: {\"value\":\"1\"}
", color="black" penwidth="2" ];
  "0x1400002b560" -> "0x1400002bc20" [label="", color="forestgreen" penwidth="3" ];
  "0x1400002bc20" [label="yield
Actions: 0, Forks: 1
State: {\"value\":\"2\"}
", color="black" penwidth="2" ];
  "0x1400002b560" -> "0x1400002bd40" [label="", color="forestgreen" penwidth="3" ];
  "0x1400002bd40" [label="yield
Actions: 0, Forks: 1
State: {\"value\":\"3\"}
", color="black" penwidth="2" ];
}
{{% /graphviz %}}


With a for loop, the value will be 6, but with any, the value can be any of 1, 2 or 3 at the end of the Init action.

### Any syntactic sugar
In many cases, if there is no step to be taken if nothing matched in the list of values,
you can use this simplified form.

{{% fizzbee %}}

action Init:
  value = 0

action Next:
  require value == 0
  x = any [1, 2, 3]
  value += x

{{% /fizzbee %}}

For more information on `require`, see the section on [guard clauses](/tutorials/guard-clause).

### Any with condition
A condition can be specified when using the any keyword. 
This is useful when you want to choose a value
{{% fizzbee %}}

action Init:
  x = any [1, 2, 3]
  y = any [1, 2, 3] : x != y

{{% /fizzbee %}}
The colon (:) here is 'such that'
The y line can be read as, choose y as any value from 1, 2, 3 such that x is not equal to y.

# Block modifiers
Block modifiers are used to specify the behavior of the block.

## Atomic
Atomic block modifier is used to specify that the block is atomic.
An atomic block is executed as a single step, without any yield points in between statements.
If two statements are executed atomically, either they both are executed or none are executed.

{{% fizzbee %}}
action Init:
  a = 0
  b = 0

action Add:
  atomic:
    a = (a + 1) % 3
    b = (b + 1) % 3

{{% /fizzbee %}}
Note: The block modifier of the top block can instead be specified at the action level,
to reduce one level of indentation. So the above code is equivalent to
  
{{% fizzbee %}}
action Init:
  a = 0
  b = 0

atomic action Add:
    a = (a + 1) % 3
    b = (b + 1) % 3
{{% /fizzbee %}}

## Oneof
Oneof block modifier indicates only one of the statements in the block will be executed.

{{% fizzbee %}}
action Init:
  a = 0
  b = 0

action Add:
  oneof:
    a = (a + 1) % 3
    b = (b + 1) % 3

{{% /fizzbee %}}

## Serial
Serial block modifier indicates the steps will be executed in sequence - one after another.
And, there will be an implicit yield point between each step. When there is an yield point,
in addition to the fact that a concurrent action can be interleaved, the system could also crash
implying the later steps may not always be executed.

{{% fizzbee %}}
action Init:
  a = 0
  b = 0

action Add:
  serial:
    a = (a + 1) % 3
    b = (b + 1) % 3

{{% /fizzbee %}}


When a block modifier is not specified, the serial block modifier is applied implicitly.

## Parallel
Parallel block modifier indicates the steps will be executed in parallel.
And, there will be an implicit yield point between each step. When there is an yield point,
in addition to the fact that a concurrent action can be interleaved, the system could also crash
implying the later steps may not always be executed.
That is, if there are two statements in a parallel block, the model checker will explore these possibilities.

- [a]
- [b]
- [a, b]
- [b, a]

{{% fizzbee %}}
action Init:
  a = 0
  b = 0

action Add:
  parallel:
    a = (a + 1) % 3
    b = (b + 1) % 3

{{% /fizzbee %}}

Run this code, you will see the state graph would show the states growing fast.

# Correctness
This is the most important part of the model checker. When exploring the state space,
we need to ensure the system does what we expect it to do.

There are two types of correctness:
- Safety: Something bad never happens. 
For example: The API should never return the wrong value.
- Liveness: Something good eventually happens.
For example: The API should eventually return a value. 

Combining these two, we can specify the correctness of the system. 
For example: The API should eventually return the correct value.

Let's take a simple example of a counter that increments by 1 until it reaches 3, then resets to 0.
But the starting value can be in `range(-2, 2)` that is oneof [-2, -1, 0, 1] .

{{% fizzbee %}}
action Init:
  value = 0
  any x in range(-2, 2):
    value = x

atomic action Add:
    if value < 3:
        value += 1
    else:
        value = 0
    
{{% /fizzbee %}}

{{% expand "Expand/collapse Graph View" %}}
{{<graphviz>}}
digraph G {
"0x14000121680" [label="Init
Actions: 0, Forks: 0

Threads: 0/1
", color="black" penwidth="1" ];
"0x14000121680" -> "0x14000121ce0" [label="", color="forestgreen" penwidth="3" ];
"0x14000121ce0" [label="yield
Actions: 0, Forks: 1
State: {\"value\":\"-2\"}
", color="black" penwidth="2" ];
"0x14000121ce0" -> "0x14000121e00" [label="Add", color="black" penwidth="1" ];
"0x14000121e00" [label="yield
Actions: 0, Forks: 1
State: {\"value\":\"-1\"}
", color="black" penwidth="2" ];
"0x14000121e00" -> "0x14000121f20" [label="Add", color="black" penwidth="1" ];
"0x14000121f20" [label="yield
Actions: 0, Forks: 1
State: {\"value\":\"0\"}
", color="black" penwidth="2" ];
"0x14000121f20" -> "0x140002000c0" [label="Add", color="black" penwidth="1" ];
"0x140002000c0" [label="yield
Actions: 0, Forks: 1
State: {\"value\":\"1\"}
", color="black" penwidth="2" ];
"0x140002000c0" -> "0x14000200ae0" [label="Add", color="black" penwidth="1" ];
"0x14000200ae0" [label="yield
Actions: 1, Forks: 2
State: {\"value\":\"2\"}
", color="black" penwidth="2" ];
"0x14000200ae0" -> "0x14000201260" [label="Add", color="black" penwidth="1" ];
"0x14000201260" [label="yield
Actions: 2, Forks: 3
State: {\"value\":\"3\"}
", color="black" penwidth="2" ];
"0x14000201260" -> "0x14000121f20" [label="Add", color="black" penwidth="1" ];
"0x14000121680" -> "0x14000121e00" [label="", color="forestgreen" penwidth="3" ];
"0x14000121680" -> "0x14000121f20" [label="", color="forestgreen" penwidth="3" ];
"0x14000121680" -> "0x140002000c0" [label="", color="forestgreen" penwidth="3" ];
}
{{< /graphviz >}}
{{% /expand %}}
## Safety
Safety is specified using the `always` keyword. In this, the safety property is, the value should never be greater than 3.

Add this code to the top of the file.
```
always assertion AlwaysLessThan3:
  return value <= 3
```
That is,
{{% fizzbee %}}
always assertion AlwaysLessThan3:
  return value <= 3

action Init:
  value = 0
  any x in range(-2, 2):
    value = x

atomic action Add:
    if value < 3:
        value += 1
    else:
        value = 0
    
{{% /fizzbee %}}

### Safety Violation
If you change the invariant to `always value <= 2`, and run the code, you will see the model checker will show a violation.
Or, change the if condition in Add from `value < 3` to `value <= 3`.

Now, the model checker will show a violation. It will print the stack trace of the behavior that lead to the failure.
You can also see the graph by clicking the link at the top of the output.

## Liveness
Liveness is specified using the `eventually` keyword. In this example, the liveness property is the value should eventually be 0.
But for most practical cases, we need to combine it with `always`. That leads to, two different possibilities:

### always eventually
This means, given enough time, the behavior will always reach the desired state eventually. For example: the above counter,
will eventually reach 0. It can go above 0, but it will again come back to 0.

always eventually value == 0
always eventually value == 1
always eventually value == 2
always eventually value == 3

### eventually always
This asserts, the behavior will reach the desired state, and stay there. For example: the above counter,
will eventually reach 0 and stay between 0 and 3 (inclusive), even though the value might
have started negative. This is expressed as:

eventually always value >= 0

## Fairness
When checking liveness, fairness is important. Actions specify what can happen in the system.
But it does not guarantee that the action will happen. Fairness is used to specify that
the action will be executed eventually.

Before we go into it, let's see the code that will violate the liveness property.


{{% fizzbee %}}
always eventually assertion BecomeZero:
  return value == 0

action Init:
  value = 0
  any x in range(-2, 2):
    value = x

atomic action Add:
    if value < 3:
        value += 1
    else:
        value = 0
    
{{% /fizzbee %}}

When you run this, you will notice the model checker will point out the liveness check failed.
You will notice something called stutter. This indicates, no action was taken after the init.

To fix this, we need to add fairness to the action Add. Fairness indicates, it will do something
useful eventually.

Change this line
```
atomic action Add:
```
to
```
atomic fair action Add:
```
Run the code, you will see the model checker will show the liveness property passed.
Open the state graph, you can see, the live nodes are marked with a green border.
And the fair transitions are marked with green arrows.


Now test the code with other liveness properties as well.

Change this line
```
always eventually assertion BecomeZero:
```
to
```
eventually always assertion BecomeZero:
```

With that, you will see, the model checker will show the liveness property failed again.
Because, the value can reach 0, but it can change to non-zero after that.

To fix it, change the liveness property to
```
eventually always assertion StayPositive:
  return value >= 0
```

### Weak Fairness
If an action is specified as `fair<weak>` or simply `fair`, it is called weak fairness.
Weak fairness is defined as "If an action is infinitely enabled, it will be executed
infinitely often". In other words, if action A is *enabled* continuously (i.e. without interruptions), 
it must eventually be taken.

### Strong Fairness
If an action is specified as `fair<strong>`, it is called strong fairness.
Strong fairness is defined as "If an action is enabled infinitely often, it will be executed
infinitely often". In other words, if action A is *enabled* continually (repeatedly, with or without interruptions),
it must eventually be taken.

We will see more details with examples of fairness later.

# Guard clauses / Enabling conditions
Guard clauses or enabling conditions are the predicates that tell whether an action/transition is allowed or not.
Guard clauses are critical to test deadlocks and liveness properties.

Some formal methods languages like Event-B, PRISM etc use explicit guard conditions. Whereas, FizzBee follows
what TLA+ does - use implicit guard conditions.

{{% fizzbee %}}
action Init:
  switch = "OFF"

atomic action On:
  if switch != "ON":
    switch = "ON"

{{% /fizzbee %}}

Run this code. The model checker will show a deadlock. Open the state graph.
You will notice that, once the `On` action is taken the first time, no other action can happen from there.

The On action is not enabled because the guard clause is false.

There are obviously two ways to fix this:
- Remove the guard clause. Then, On will always be enabled.
- Add another action that will turn off the switch.

1. Remove the guard clause.
{{% fizzbee %}}
action Init:
  switch = "OFF"

atomic action On:
    switch = "ON"
{{% /fizzbee %}}
Run the code. Open the state graph, you will see the On has a link to itself.

2. Add another action to turn off the switch.

{{% fizzbee %}}
action Init:
  switch = "OFF"

atomic action On:
  if switch != "ON":
    switch = "ON"

atomic action Off:
  if switch != "OFF":
    switch = "OFF"

{{% /fizzbee %}}

{{< hint type=note >}}
Implementation note: an action is enabled if there is at least one simple statement executed - that's it.
{{< /hint >}}

## Nested guard clauses
Guard clauses do not have to be at the top level. They can be nested inside a block,
within loops, within a function that gets called and so on. 

{{% fizzbee %}}
action Init:
  has_even = False

atomic action FindEven: 
  for x in [1, 3, 5]:
    if x % 2 == 0:
      has_even = True
{{% /fizzbee %}}

For the mathematically inclined, *this is equivalent to saying, 
there exists a number x in the list [1, 3, 5] such that x is even.* which is obviously false.

## require keyword
Sometimes, it is convenient to explicitly specify the guard clause with `require` keyword.
That would reduce the extra indentation.

{{% fizzbee %}}
action Init:
  switch = "OFF"

atomic action On:
  require switch != "ON"
  switch = "ON"

atomic action Off:
  require switch != "OFF"
  switch = "OFF"

{{% /fizzbee %}}
Although this might look like a simple if condition, it is not in some cases.

For example: the require statement aborts the current fork completely. So, when used within a loop, 
the entire fork would be abandoned. So, when used within a for loop, require would imply the entire loop is abandoned (not just return/continue).

{{% fizzbee %}}
action Init:
  has_even = False

atomic action FindEven:
  for x in [2, 3, 5]:
    require x % 2 == 0
    has_even = True

#atomic action FindEven:
#  for x in [2, 3, 5]:
#    if x % 2 == 0:
#      has_even = True
{{% /fizzbee %}}

When you run it, you will see, even though `2` is even, the `require` is expecting
every element in the list to be even.

## Guard clauses with fairness
Guard clauses define whether an action is enabled. Fairness defines whether an action will be taken if enabled.

### Weak fairness
As defined earlier, weak fairness is defined as 
"If an action is infinitely enabled, it will be executed infinitely often".

Look at this example: 
{{% fizzbee %}}
action Init:
  status = "idle"

atomic action Process:
  if status == "idle":
    status = "working"

atomic action Finish:
  if status == "working":
    status = "idle"

atomic action Fail:
  status = "failed"

{{% /fizzbee %}}

Open the state graph. There is a cycle between idle <--> working. But from either of these
cases, the system can reach `failed` state. So, from within the cycle, the action `Fail` is enabled
continuously without interruption. That means, weak fairness will be satisfied.

Add a liveness property and fairness that the system will reach failed stated as an excercise

{{% expand "Show code" %}}

1. Add this Assertion
{{< highlight python >}}
eventually always assertion Fail:
  return status == "failed"
{{< /highlight >}}

2. Change the Fail action to be fair
{{< highlight python >}}

atomic fair action Fail:
  status = "failed"
{{< /highlight >}}

{{% hint type=warning %}}
This example is just to demonstrate the concept of fairness. In a real system, the failed state
is the not desired state. So, the fairness requirement on the Fail action should be removed.

{{% /hint %}}

{{% /expand %}}


### Strong fairness
As defined earlier, strong fairness is defined as
"If an action is enabled infinitely often, it will be executed infinitely often"

In the previous example, let us say, a system can be shutdown if it is idle.
(Let is remove the failed state for now)

{{% fizzbee %}}
action Init:
  status = "idle"

atomic action Process:
  if status == "idle":
    status = "working"

atomic action Finish:
  if status == "working":
    status = "idle"

atomic action Shutdown:
  if status != "working":
    status = "shutdown"

{{% /fizzbee %}}

Open the state graph. Notice that, in the cycle "idle" <--> "working", Shutdown action
can only happen from "idle" state. So here weak fairness will not be sufficient to ensure
the system will eventually be shutdown.

Add a liveness property and fairness that the system will reach failed stated as an excercise

{{% expand "Show code" %}}

1. Add this Assertion
{{< highlight python >}}
eventually always assertion SafelyShutdown:
  return status == "shutdown"
{{< /highlight >}}

2. Change the Process action to be `fair<weak>` or just `fair`
{{< highlight python >}}
  atomic fair action Finish:
    if status == "working":
      status = "idle"
{{< /highlight >}}
Weak fair is sufficient here, because once the `working` state is reached,
the `Finish` action will be always enabled.

3. Change the Shutdown action to be `fair<strong>`
{{< highlight python >}}
atomic fair<strong> action Shutdown:
  if status != "working":
    status = "shutdown"
{{< /highlight >}}
Here, strong fairness is required because once the `idle` state is reached,
the `Shutdown` will be enabled. But the system can switch to the working state,
at that point, the `Shutdown` action is not enabled. So the system can effectively,
switch between `idle` and `working` states without ever reaching the `shutdown` state.



{{% /expand %}}

# Exercise 1: Liveness

(Extending the previous example) Model a request processing system.
1. The system starts in an _idle_ state, and when there is work, it gets to work.
2. The system can be _shutdown_ when it is _idle_.
3. The system can fail any time it is ON.
4. The failed system will be fixed eventually, on fixing, it gets to idle state
5. A shutdown system will be restarted eventually
6. Check for liveness condition that the system will be in 'working' eventually.

{{% expand "Show code" %}}
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


{{< /expand >}}

{{< hint >}}
When designing the system, try to reduce the fairness requirements. We must model the system
that can be implemented. From an implementation perspective, Fairness indicates things
that must go right. 

- Weak fairness is usually easier to implement than strong fairness.
- Fewer fair actions usually means easier to implement correctly

{{< /hint >}}
