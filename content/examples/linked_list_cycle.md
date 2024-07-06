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

In this post, we will model [Floyd's tortoise and hare](https://en.wikipedia.org/wiki/Cycle_detection#Floyd's_tortoise_and_hare) algorithm for cycle detection and an algorithm that keeps track of the visited nodes to find cycles.

## Problem statement:

- Given a linked list that may contain a cycle
- The algorithm should detect the cycle if it exists

## Algorithm

- Let there be two pointers called `slow` and `fast`
- Choose any node in the linked list
- Both pointers point to the chosen node at first
- In each step of the algorithm, the `slow` pointer advances to the next node and the `fast` pointer advances to the next next node.
- At any point in time, if both pointers point to the same node, a cycle has been found. If any of the pointers reached the end of the list, there's no cycle.

## How to model it with FizzBee

The linked list model won't use pointers. It'll be a map called `succ` where nodes are keys and the value associated to the key is the node's successor in the list.

Given a list `A -> B -> C`, `succ` would look like this:
```python
succ = {'A': 'B', 'B': 'C', 'C': None}
```

{{% hint type=note %}}
C has None as its successor because it is the last element in the list.
{{% /hint %}}

## Implementation

We can start by generating a linked list that may contain a cycle.

{{% fizzbee %}}
POSSIBLE_NODES = list(range(1, 4))

action Init:
  # A dict from node to its successor.
  # Example: {1: 2, 2: 3, 3: None}
  succ = {}
  current = any POSSIBLE_NODES
  has_cycle = False
  while (current and not has_cycle):
    next = any list(POSSIBLE_NODES) + [None]
    succ[current] = next  
      
    has_cycle = next in succ
    current = next  

  nodes = succ.keys()
  start = any nodes
{{% /fizzbee %}}

We set `has_cycle` to `True` when a list that contains a cycle is generated.  

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

### Floyd's algorithm

The algorithm can be implemented using a single atomic function.

```python
atomic func tortoise_and_hare():
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
```

### Finding cycle by keeping track of visited nodes

We can also use an algorithm that keeps track of viisted nodes to detect cycles and compare the result with the algorithm we are modeling.  

```python
atomic func find_cycle_by_keeping_visited_set():
  current = start

  visited = set()

  while current != None:
    if current in visited:
      return True
    visited.add(current)
    current = succ.get(current)

  return False
```

### Safety invariants

Since the both algorithms return `True` or `False`, the assertion for each algorithm can just check that the algorithm returns the expected result.

```python
always assertion TortoiseAndHareFindsCycle:
  found = tortoise_and_hare()
  return has_cycle == found

always assertion VisitedSetFindsCycle:
  found = find_cycle_by_keeping_visited_set()
  return has_cycle == found
```

## Full code

{{% fizzbee %}}
POSSIBLE_NODES = list(range(1, 4))

always assertion TortoiseAndHareFindsCycle:
  found = tortoise_and_hare()
  return has_cycle == found

always assertion VisitedSetFindsCycle:
  found = find_cycle_by_keeping_visited_set()
  return has_cycle == found

action Init:
  # A dict from node to its successor.
  # Example: {1: 2, 2: 3, 3: None}
  succ = {}
  current = any POSSIBLE_NODES
  has_cycle = False
  while (current and not has_cycle):
    next = any POSSIBLE_NODES + [None]
    succ[current] = next  
      
    has_cycle = next in succ
    current = next  

  nodes = succ.keys()
  start = any nodes

atomic func find_cycle_by_keeping_visited_set():
  current = start

  visited = set()

  while current != None:
    if current in visited:
      return True
    visited.add(current)
    current = succ.get(current)

  return False

atomic func tortoise_and_hare():
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
