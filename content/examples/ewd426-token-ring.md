---
title: EWD426 Token Ring
weight: 10
---

# EWD426 Dijkstra's Self Stabilizing Token Ring Algorithm

This is a classic distributed algorithm by Edsger W. Dijkstra to solve the token ring problem,
that started the field of self-stabilization in distributed systems.

The algorithm is a self-stabilizing algorithm, which means it can recover from any transient faults.
And once recovered it remains in the stable state (until next disruption)

{{< toc >}}

## Problem statement
There is a ring of servers and to access a shared resource, a token is passed around the ring.
Whoever has the token can access the shared resource.

In the valid state, there must be only one token in the ring.
There can be two types of invalid states:
- No token in the ring
- More than one token in the ring

The goal is to design an algorithm that can recover from any invalid state and reach the valid state.

## Dijkstra's Self Stabilizing Token Ring Algorithm

Dijkstra came up with an ingenious algorithm to solve this - by specifying
how to represent the token.

In his model, each server has access to the left side neighbor, and each server
holds a key. If the key of a server is different from its left side neighbor, then
the server has the token. That is, if value[i] != value[i-1], then server i has the token.

Being a ring, for the 0th server, the left side neighbor is the last server.
But the rules for holding the token is the opposite for the 0th server.
That is, if value[0] == value[n-1] where n is the number of servers in the ring,
then the 0th server has the token.

By this formulation, there is no way to have 0 tokens. If all the values are the same,
then only the server 0 has the token.
This rules out the invalid state of having 0 tokens.

To reach a state where server 0 has the token, all the values must be the same.

### How to pass the token from 0 to 1?
All we need to do is to change the value of server 0 to a new value. Then the token will be passed to server 1.
That is, from [x, x, x, x, x, x] to [y, x, x, x, x, x] where y != x.

### How to pass the token from 1 to 2?
Following the same logic, change the value of server 1 to a new value.
That is, from [y, x, x, x, x, x] to [y, z, x, x, x, x] where z != x.
In this case, there is actually two tokens in the ring. 
Because value[1] != value[0], server 1 has the token
and value[1] != value[2], so the server 2 has the token.

### How to remove the token from the server 1?
Set it to the same value as the left side neighbor. 
That is, from [y, z, x, x, x, x] to [y, y, x, x, x, x]
Notice, the server 2 still has the token because y != x.

### Generalizing for all servers except the 0th server
At this point, we can generalize it to all servers != 0.
To pass the token, just copy the value of the left side neighbor.
It would look like this:
[y, y, ..., y, x, x, ... , x, x]

Technically, this algorithm can use any data type for the value, but
for simplicity, we will use integers and for model checking, we would also
have to restrict the range of possible values - [0, n-1] where n is the number of servers.

## Implementation

The only critical state is the counters. We represent them just as an array of integers.

### Represent counters
```python
    counters = [0] * N
```

### Initialize to all possible values

Iterate over each server / array, set the value to be any value
between 0 and M-1. 
This is a good example to show the `for` and `any` keywords.
The `for` is exactly to python's `for`, and equivalent to \A TLA+ operator.  
The `any` is the equivalent of \E TLA+ operator. Basic idea is, it is a multiverse.
Every non-deterministic choice creates a parallel universe.


```python
    for i in NODES:
        any j in range(0, M):
            counters[i] = j
```

This code will create 3 possible paths, one for each of the values 0, 1, 2.
```python
    any j in [0, 1, 2]:
      value = j
```

{{% hint type=note %}}
In FizzBee, the variables declared at the top are treated as constants. To declare the
actual state variables, initialize them within the action.
{{% /hint %}}

{{% fizzbee %}}
# Globally declared variables are constants
N = 4  # Number of servers
M = 3  # Number of possible values
NODES = range(0, N)


atomic action Init:
    # state variables are declared with the global action Init
    counters = [0] * N
    for i in NODES:
        any j in range(0, M):
            counters[i] = j
{{% /fizzbee %}}

Run this code, and see the possible states generated.
Also, check the total number of actual init states and the internal states as well.

If you notice, the number of leaf nodes is M^N = 3^4 = 81, which is the total number of possible states.
If you include the internal states, it would be (M^(N+1) - 1) / (M - 1) = (3^5-1)/(3-1) = 81.

#### Exercise 1: Change the values of M and N and see the impact on the number of states generated.
Of course do the math first, and then run the code to see if the generated states match the calculated states.

#### Exercise 2: Add an invariant, that there will always be at least 1 token.

{{% expand "Show solution" %}}
{{< highlight python >}}
always assertion HasTokens:
    tokens = 0
    if counters[0] == counters[N-1]:
        # 0 has token
        tokens += 1
    for i in range(1, N):
        if counters[i] != counters[i-1]:
            # i has token
            tokens += 1
    return tokens >= 1
{{< /highlight >}}
{{% /expand %}}

### Pass the token from 0 to 1
This is a special case, but the easy one, we will start with this.

Server 0 can pass the token to 1, only if server 0 has the token.
In other words, the guard condition is, the value of 0 is same as the value of N-1.
To pass the value, just increment the value and roll over if it is over M.

{{% highlight python %}}
  if counters[0] == counters[N-1]:
    counters[0] = (counters[N-1] + 1) % M
{{% /highlight %}}


### Pass the token from i to i + 1

{{% highlight python %}}
  # When i != 0  
  if counters[i] != counters[i-1]:
    counters[i] = counters[i-1]
{{% /highlight %}}

## PassToken action

{{% highlight python %}}
atomic  action PassToken:
  # some code here
{{% /highlight %}}

The tokens are not passed in a lock step. So, each server can pass the token to the next server
independently as long as the server has the token. 

Any server can take the next action is modeled with the `any` keyword, obviously.

{{% highlight python "hl_lines=2 3 5"%}}
atomic  action PassToken:
  any i in NODES:
    if i == 0:
      # Handle 0th node special case
    else:
      # Handle all other nodes
{{% /highlight %}}

Since the token is passed only if the server has the token, we need to add the guard condition.
{{% highlight python "hl_lines=4 7"%}}
atomic  action PassToken:
  any i in NODES:
    if i == 0:
      if counters[0] == counters[N-1]:
        # pass the token
    else:
      if counters[i] != counters[i-1]:
        # pass the token
{{% /highlight %}}

Finally, passing the token is simply copying the value of the left side neighbor, or incrementing the value for the 0th node.
{{% highlight python "hl_lines=5 8"%}}
atomic action PassToken:
  any i in NODES:
    if i == 0:
      if counters[0] == counters[N-1]:
        counters[0] = (counters[N-1] + 1) % M
    else:
      if counters[i] != counters[i-1]:
        counters[i] = counters[i-1]
      
{{% /highlight %}}

That's it. The token is passed from i to i+1.

The complete code would look like this:

{{% fizzbee %}}

N = 4
M = 3
NODES = range(0, N)

atomic action Init:
    counters = [0] * N
    for i in NODES:
        any j in range(0, M):
            counters[i] = j

atomic action PassToken:
  any i in NODES:
    if i == 0:
      if counters[0] == counters[N-1]:
        counters[0] = (counters[N-1] + 1) % M
    else:
      if counters[i] != counters[i-1]:
        counters[i] = counters[i-1]


always assertion HasTokens:
    tokens = 0
    if counters[0] == counters[N-1]:
        # 0 has token
        tokens += 1
    for i in range(1, N):
        if counters[i] != counters[i-1]:
            # i has token
            tokens += 1
    return tokens >= 1

{{% /fizzbee %}}

Run the above code and see the possible states generated.
{{% hint %}}
Play with the state space and again convince yourself that
the number of tokens will never be 0.
{{% /hint %}}

### Self-stabilization assertion
This is the critical part of the algorithm that verifies the system
stabilizes into a valid state.

Since this is not something that is always true, but we want to check if it 
eventually becomes true.

{{% highlight udiff %}}

-always assertion HasTokens:
+eventually always assertion UniqueToken:
     tokens = 0
     if counters[0] == counters[N-1]:
         # 0 has token
@@ -7,5 +7,5 @@
         if counters[i] != counters[i-1]:
             # i has token
             tokens += 1
-    return tokens >= 1
+    return tokens == 1
{{% /highlight %}}

Run the code. This liveness check will fail due to stuttering.

Add fairness to the actions. We just need weak fairness.

{{% highlight udiff %}}
@@ -1,8 +1,8 @@

-atomic action PassToken:
+atomic fair action PassToken:
     any i in NODES:
{{% /highlight %}}

Run the code again. This time, the liveness check will pass.

### Exercise 3: Change the values of M and N
Change the values of M and N, and notice how the state spaces grow, and
when the system never stabilizes.

{{% expand "Show solution" %}}
For this algorithm to stabilize N >= M - 1
Check with N = 4, and M = 2 and see why it never stabilizes.
{{% /expand %}}

## Complete Code
{{% expand "Show full code" %}}
{{< fizzbee >}}
N = 4
M = 3
NODES = range(0, N)

atomic action Init:
    counters = [0] * N
    for i in NODES:
        any j in range(0, M):
            counters[i] = j

atomic fair action PassToken:
    i = any NODES
    if i == 0:
      if counters[0] == counters[N-1]:
        counters[0] = (counters[N-1] + 1) % M
    else:
      if counters[i] != counters[i-1]:
        counters[i] = counters[i-1]


eventually always assertion UniqueToken:
    tokens = 0
    if counters[0] == counters[N-1]:
        # 0 has token
        tokens += 1
    for i in range(1, N):
        if counters[i] != counters[i-1]:
            # i has token
            tokens += 1
    return tokens == 1

{{< /fizzbee >}}
{{% /expand %}}

## Alternate modeling using roles
While the above representation works and sufficient for this problem, many distributed algorithms are
expressed naturally using roles.

{{% fizzbee %}}

N = 4
M = 3
NODES = range(0, N)

role Node:
    action Init:
        i = any range(M) # can't assign to self.counter directly
        self.counter = i

    atomic fair action PassToken:
        if self.ID == 0:
          if self.counter == nodes[N-1].counter:
            self.counter = (nodes[N-1].counter + 1) % M
        else:
          if self.counter != nodes[self.ID-1].counter:
            self.counter = nodes[self.ID-1].counter

atomic action Init:
    nodes = []
    for i in NODES:
        nodes.append(Node(ID=i))

eventually always assertion UniqueToken:
    tokens = 0
    if nodes[0].counter == nodes[N-1].counter:
        # 0 has token
        tokens += 1
    for i in range(1, N):
        if nodes[i].counter != nodes[i-1].counter:
            # i has token
            tokens += 1
    return tokens == 1

{{% /fizzbee %}}

## Comparsion with other formal languages

### PlusCal
https://muratbuffalo.blogspot.com/2015/01/dijkstras-stabilizing-token-ring.html

### TLA+
https://muratbuffalo.blogspot.com/2022/10/checking-statistical-properties-of.html

Full code here: https://github.com/tlaplus/Examples/blob/master/specifications/ewd426/TokenRing.tla

Note: In the TLA+ code, the UniqueToken assertion is expressed in functional style the way
mathematicians would write it. If you want to express it the same way.

{{% highlight python %}}

eventually always assertion Stabilized:
  return any(
              [ all([counters[j] == counters[0] for j in range(0,i)]) and
                all([counters[j] == (counters[0]-1)%M for j in range(i,N)])
                  for i in range(N+1)
              ]
            )
{{% /highlight %}}

