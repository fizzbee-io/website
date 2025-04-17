---
title: Die Hard
weight: 10
---

# Die Hard Water Jug Problem

This is a good example to understand the grammar and state exploration of FizzBee.

This problem is from the movie Die Hard 3, 
where Bruce Willis and Samuel L. Jackson are given a task to measure 
4 gallons of water using a 3-gallon and a 5-gallon jug.

Watch it here. https://youtu.be/6cAbgAaEOVE

This is also a known example from TLA+ video tutorial - so if you are familiar with
TLA+ most likely you have done this example.

{{< toc >}}

## Problem statement
- You have a 3-litre jug and a 5-litre jug.
- Infinite water supply.
- You need to measure 4 litres of water.
Find the [shortest] steps to measure 4 litres of water.

## How to model it with FizzBee

For these modeling problems, we need to define the state and the actions that can be performed on the state.

### States
- Amount of water in the 3-litre jug
- Amount of water in the 5-litre jug

### Actions 
- Fill the 3-litre jug
- Fill the 5-litre jug
- Empty the 3-litre jug
- Empty the 5-litre jug
- Pour water from the 3-litre jug to the 5-litre jug
- Pour water from the 5-litre jug to the 3-litre jug

### Stopping condition as Invariants
This is an unusual example - technically, we need to find the shortest path to reach the goal.
So, instead of defining the invariant as what we want to be always true, we define 
the invariant as what should hold true to keep continuing - that is negation of end state.

That we stop when the 4 litres of water in the big jug.

## Implementation

### States
Let us define two variables big and small for the two jugs, and start with both empty.

{{% highlight python %}}
action Init:
  big = 0
  small = 0

{{% /highlight %}}

### Actions

#### Fill the 3-litre jug
Filling the 3-litre jug is simple - just set the small to 3.

{{% highlight python %}}
atomic action FillSmall:
    small = 3
{{% /highlight %}}

#### Fill the 5-litre jug
Set the big to 5.

{{% highlight python %}}
atomic action FillBig:
    big = 5
{{% /highlight %}}

#### Empty the 3-litre jug
Set the small to 0.

{{% highlight python %}}
atomic action EmptySmall:
    small = 0
{{% /highlight %}}

#### Empty the 5-litre jug
Set the big to 0.

{{% highlight python %}}
atomic action EmptyBig:
    big = 0
{{% /highlight %}}

#### Pour water from the 3-litre jug to the 5-litre jug
This is a bit tricky. We need to check if the small jug has water 
and the big jug is not full. If it has any remaining water, it should remain in the small jug.

{{% highlight python %}}
atomic action SmallToBig:
    if small + big <= 5:
        # There is enough space in the big jug
        big = big + small
        small = 0
    else:
        # There is not enough space in the big jug
        small = small - (5 - big)
        big = 5
{{% /highlight %}}

#### Pour water from the 5-litre jug to the 3-litre jug
This is similar to the previous action, but in the opposite direction.

{{% highlight python %}}
atomic action BigToSmall:
    if small + big <= 3:
        # There is enough space in the small jug
        small = big + small
        big = 0
    else:
        # There is not enough space in the small jug
        big = big - (3 - small)
        small = 3
{{% /highlight %}}


### Invariants
We need to define the stopping condition as invariants.

{{% highlight python %}}
always assertion NotFour:
  return big != 4
{{% /highlight %}}

### Full code

{{% fizzbee %}}
always assertion NotFour:
  return big != 4

action Init:
  big = 0
  small = 0

atomic action FillSmall:
  small = 3

atomic action FillBig:
  big = 5

atomic action EmptySmall:
  small = 0

atomic action EmptyBig:
  big = 0

atomic action SmallToBig:
    if small + big <= 5:
        # There is enough space in the big jug
        big = big + small
        small = 0
    else:
        # There is not enough space in the big jug
        small = small - (5 - big)
        big = 5

atomic action BigToSmall:
    if small + big <= 3:
        # There is enough space in the small jug
        small = big + small
        big = 0
    else:
        # There is not enough space in the small jug
        big = big - (3 - small)
        small = 3
{{% /fizzbee %}}

Take a look at the trace that leads to the 4 litres of water in the big jug.
It took 6 steps to reach the goal, each corresponding to each of the defined actions.

{{% graphviz %}}
digraph G {
  "0" [label="yield
Actions: 0, Forks: 0
State: {\"big\":\"0\",\"small\":\"0\"}
", color="black" penwidth="2" ];
  "1" [label="yield
Actions: 1, Forks: 1
State: {\"big\":\"5\",\"small\":\"0\"}
", color="black" penwidth="2" ];
  "0" -> "1" [label="FillBig"];
  "2" [label="yield
Actions: 2, Forks: 2
State: {\"big\":\"2\",\"small\":\"3\"}
", color="black" penwidth="2" ];
  "1" -> "2" [label="BigToSmall"];
  "3" [label="yield
Actions: 3, Forks: 3
State: {\"big\":\"2\",\"small\":\"0\"}
", color="black" penwidth="2" ];
  "2" -> "3" [label="EmptySmall"];
  "4" [label="yield
Actions: 4, Forks: 4
State: {\"big\":\"0\",\"small\":\"2\"}
", color="black" penwidth="2" ];
  "3" -> "4" [label="BigToSmall"];
  "5" [label="yield
Actions: 5, Forks: 5
State: {\"big\":\"5\",\"small\":\"2\"}
", color="black" penwidth="2" ];
  "4" -> "5" [label="FillBig"];
  "6" [label="BigToSmall
Actions: 6, Forks: 6
State: {\"big\":\"4\",\"small\":\"3\"}
", color="red" penwidth="2" ];
  "5" -> "6" [label="BigToSmall"];
}
{{% /graphviz %}}

## Compare with TLA+

Equivalent [implementation in TLA+](https://github.com/tlaplus/Examples/blob/master/specifications/DieHard/DieHard.tla
).
Stripped out the comments for brevity. Take a look at the github link for the code
with the comments.

```tla
------------------------------ MODULE DieHard ------------------------------- 
EXTENDS Naturals
  
VARIABLES big,   
          small  

TypeOK == /\ small \in 0..3 
          /\ big   \in 0..5

Init == /\ big = 0 
        /\ small = 0

FillSmallJug  == /\ small' = 3 
                 /\ big' = big

FillBigJug    == /\ big' = 5 
                 /\ small' = small

EmptySmallJug == /\ small' = 0 
                 /\ big' = big

EmptyBigJug   == /\ big' = 0 
                 /\ small' = small

Min(m,n) == IF m < n THEN m ELSE n

SmallToBig == /\ big'   = Min(big + small, 5)
              /\ small' = small - (big' - big)

BigToSmall == /\ small' = Min(big + small, 3) 
              /\ big'   = big - (small' - small)

Next ==  \/ FillSmallJug 
         \/ FillBigJug    
         \/ EmptySmallJug 
         \/ EmptyBigJug    
         \/ SmallToBig    
         \/ BigToSmall    

Spec == Init /\ [][Next]_<<big, small>> 
-----------------------------------------------------------------------------

NotSolved == big # 4

=============================================================================
```

## Exercises

### 1. Reduce the number of possible actions
We have defined all possible actions. To find the shortest number of steps, we must use each of these actions once.

Can you reduce the number of actions and see if we can still find a solution? The solution might take
more steps as it might have to repeat some actions.

### 2. Reduce some unnecessary actions in state graph
Open the state graph, you might see that there are many transitions that are not necessary that are also explored.
For example: Emptying a jug that is already empty, filling a jug that is already full, etc.

You can reduce these unnecessary steps by adding guard conditions to the actions.
{{% highlight python %}}
atomic action FillSmall:
  if small < 3:
    small = 3
{{% /highlight %}}
Do this to all other actions, to see the impact on the generated graphs.
{{% hint %}}
For this problem, it has no effect. But for some real problems, guard conditions would
be critical to find deadlocks
{{% /hint %}}
