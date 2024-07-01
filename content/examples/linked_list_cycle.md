---
title: Linked List cycle
weight: 10
---

# Detect cycle in a linked list

A [linked list](https://en.wikipedia.org/wiki/Linked_list) is linear collection of elements where each element points to the next.

A linked list may have a cycle if one of the elements points to an element that's already in the list.

Here' a few examples of linked lists that contain cycles:

```
A <-> A
A -> B -> A
A -> B -> B
A -> B -> C -> A
A -> B -> C -> B
```

and a few examples of linked lists that don't contain cycles:

```
A
A -> B
A -> B -> C
```

{{% hint type=note %}}
A -> B means that node A points to node B.
{{% /hint %}}

In this post, we will model [Floyd's tortoise and hare](https://en.wikipedia.org/wiki/Cycle_detection#Floyd's_tortoise_and_hare) algorithm for cycle detection.

## Problem statement:

- Given a linked list that may contain a cycle
- Floyd's algorithm should detect the cycle if it exists

## Algorithm

- Let there be two pointers called `slow` and `fast`
- Choose any node in the linked list
- Both pointers point to the chosen node at first
- In each step of the algorithm, the `slow` pointer advances to the next node and the `fast` pointer advances to the next next node.
- At any point in time, if both pointers point to the same node, a cycle has been found. If any of the pointers reached the end of the list, there's no cycle.

## How to model it with FizzBee

The linked list model won't use pointers. It'll be a map called `succ` where nodes are keys and the value associated to the key is the node's successor in the list.

Given a list `A -> B -> C`, `succ` would look like this:
{{% fizzbee %}}
succ = {'A': 'B', 'B': 'C', 'C': None}
{{% /fizzbee %}}

{{% hint type=note %}}
C has None as its successor because it is that last element in the list.
{{% /hint %}}

## Implementation

We can start by generating a linked list that may contain a cycle.

{{% fizzbee %}}
action Init:
  hasCycle = False

  possibleNodes = range(1, 4)

  current = any possibleNodes

  # A dict from node to its successor.
  # Example: {1: 2, 2: 3, 3: None}
  succ = {}

  while True:
    # The current node points to either:
    oneof:
      # None, which means the current pointer is the last one in the list.
      atomic: 
        succ[current] = None 
        break
      # Any other node, including itself.
      atomic:
        next = any possibleNodes
        succ[current] = next
        # If the current node is now pointing to a node that's already in the list,
        # a cycle has been created, we can exit the loop.
        if next in succ:
          hasCycle = True
          break
        succ[next] = None
        current = next

  nodes = succ.keys()
  start = any nodes
{{% /fizzbee %}}

We set `hasCycle` to `True` when a list that contains a cycle is generated.  

If we add `print(succ)` at the end of `Init` we'll see that every possible list with and without cycles is being generated:  
```
{1: None}
{2: None}
{3: None}
{1: 1}
{2: 2}
{3: 3}
{1: 2, 2: None}
{1: 2, 2: None}
{1: 3, 3: None}
{1: 3, 3: None}
{2: 1, 1: None}
{2: 1, 1: None}
{2: 3, 3: None}
{2: 3, 3: None}
{3: 1, 1: None}
{3: 1, 1: None}
{3: 2, 2: None}
{3: 2, 2: None}
{1: 2, 2: 1}
{1: 2, 2: 1}
{1: 2, 2: 2}
{1: 2, 2: 2}
{1: 3, 3: 1}
{1: 3, 3: 1}
{1: 3, 3: 3}
{1: 3, 3: 3}
{2: 1, 1: 1}
<rest of output omitted for brevity>
```

The algorithm itself can be implemented using a single atomic function.

{{% fizzbee %}}
atomic func tortoiseAndHare():
  tortoise = start
  hare = start

  while True:
    # If the slow pointer has not reached the end of the list. Advance it by 1.
    if tortoise != None:
      tortoise = succ.get(tortoise)

    # Advance the fast pointer by 2.
    for _ in range(0, 2):
      if hare != None:
        hare = succ.get(hare)
          
    if tortoise == None or hare == None:
      return False
      
    if tortoise == hare:
      return True
{{% /fizzbee %}}

We can also use an algorithm that keeps track of viisted nodes to detect cycles and compare the result with the algorithm we are modeling.  

{{% fizzbee %}}
atomic func findCycleByKeepingVisitedSet():
  current = start

  visited = set()

  while current != None:
    if current in visited:
      return True
    visited.add(current)
    current = succ.get(current)

  return False
{{% /fizzbee %}}

### Safety invariants

Since the algorithm only returns `True` or `False`, the assertion can just check if the algorithm function returns the expecte result for each of the lists generated.

{{% fizzbee %}}
always assertion FindsCycle:
  hasCycle1 = findCycleByKeepingVisitedSet()
  hasCycle2 = tortoiseAndHare()
  return hasCycle == hasCycle1 and hasCycle == hasCycle2
{{% /fizzbee %}}

## Full code

{{% fizzbee %}}
always assertion FindsCycle:
  hasCycle1 = findCycleByKeepingVisitedSet()
  hasCycle2 = tortoiseAndHare()
  return hasCycle == hasCycle1 and hasCycle == hasCycle2

action Init:
  hasCycle = False

  possibleNodes = range(1, 4)

  current = any possibleNodes

  # A dict from node to its successor.
  # Example: {1: 2, 2: 3, 3: None}
  succ = {}

  while True:
    # The current node points to either:
    oneof:
      # None, which means the current pointer is the last one in the list.
      atomic: 
        succ[current] = None 
        break
      # Any other node, including itself.
      atomic:
        next = any possibleNodes
        succ[current] = next
        # If the current node is now pointing to a node that's already in the list,
        # a cycle has been created, we can exit the loop.
        if next in succ:
          hasCycle = True
          break
        succ[next] = None
        current = next

  nodes = succ.keys()
  start = any nodes

atomic func findCycleByKeepingVisitedSet():
  current = start

  visited = set()

  while current != None:
    if current in visited:
      return True
    visited.add(current)
    current = succ.get(current)

  return False

atomic func tortoiseAndHare():
  tortoise = start
  hare = start

  while True:
    # If the slow pointer has not reached the end of the list. Advance it by 1.
    if tortoise != None:
      tortoise = succ.get(tortoise)

    # Advance the fast pointer by 2.
    for _ in range(0, 2):
      if hare != None:
        hare = succ.get(hare)
          
    if tortoise == None or hare == None:
      return False
      
    if tortoise == hare:
      return True

action NoOp:
    pass
{{% /fizzbee %}}

## Compare with TLA+

This example was inspired this [post](https://surfingcomplexity.blog/2017/10/16/the-tortoise-and-the-hare-in-tla/) by Lorin Hochstein which models Floyd's algorithm in TLA+.

Remember, FizzBee is a multi-paradigm language, so you can use the style that suits you best.
