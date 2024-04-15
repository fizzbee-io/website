---
title: Publish algorithms with testable code
type: posts
date: 2024-04-12
tags:
  - python
  - pseudocode
---


In March 2023, Andrew Helwer wrote a thought-provoking article comparing
[Python with PlusCal & TLA+](https://ahelwer.ca/post/2023-03-30-pseudocode/), 
while implementing a 45-year-old algorithm. 

Reflecting on his insights, I find myself resonating with much of what he shared. 
Indeed, when it comes to publishing algorithms, opting for an executable language
over arbitrary pseudocode stands out as a superior choice.

A quick recap from his article:
> Python made a very compelling case for itself here. The final 
> algorithm, naive algorithm, and property-based testing code 
> combined took up only 35 very readable lines!

On PlusCal,
> It [PlusCal] ran around 275 lines (100 of those generated) 
> split across four source files just to match Python’s 35-line execution & test functionality. 
> Also, it took more effort to write: 
> probably an entire day of work for the basics plus another day for polish, 
> vs. less than an hour for the Python version.

Of course, he did highlight,
> To be fair, sequential string algorithms are not PlusCal’s strength. 
> It really shines in concurrent & distributed algorithms, where 
> the model checker explores all possible interleavings of instructions.

Andrew's post was one of the inspirations for FizzBee (He was also among the first
who looked at FizzBee code when all I had were a few slides). 

{{< rawhtml >}}
<div style="width:360px;max-width:100%;margin:0 auto;"><div style="height:0;padding-bottom:75.83%;position:relative;"><iframe width="360" height="273" style="position:absolute;top:0;left:0;width:100%;height:100%;" frameBorder="0" src="https://imgflip.com/embed/8mmp9c"></iframe></div><p><a href="https://imgflip.com/gif/8mmp9c">via Imgflip</a></p></div>
{{</rawhtml>}}


- Python's ease of use
- PlusCal's model checking capabilities

Why not both?

That thought led to FizzBee - a formal specification language and model checker that seamlessly merges 
Python's ease of use with PlusCal's powerful model checking capabilities.

As much as possible, I tried to keep the syntax similar to Python.

Let me show the same algorithm in FizzBee.

I am literally copying the Python code from Andrew's post and pasting it here.
The only change needed here is, the func definition, and mark the function as atomic.

First the buggy algorithm:

```python
# Replace 'def lcs(b):' with 'atomic func lcs(b):'
atomic func lcs(b):
    n = len(b)
    f = [-1] * (2 * n)
    k = 0
    for j in range(1, 2 * n):
        if j - k >= n:
            return k
        i = f[j - k - 1]
        while b[j % n] != b[(k + i + 1) % n] and i != -1:
            if b[j % n] < b[(k + i + 1) % n]:
                k = j - i - 1
            i = f[i]
        if b[j % n] != b[(k + i + 1) % n] and i == -1:
            if b[j % n] < b[(k + i + 1) % n]:
                k = j
            f[j - k] = -1
        else:
            f[j - k] = i + 1
    return k
```

Assertion:

```python
always assertion LcsMatchNaiveLcs:
  expected = naive_lcs(input)
  actual = lcs(input)
  return actual == expected

atomic func naive_lcs(s):
    n = len(s)
    if n == 0:
        return 0
    rotations = [s[i:] + s[:i] for i in range(n)]
    least_rotation = min(rotations)
    return rotations.index(least_rotation)

```
Driver code:
We just need to initialize the input to all possible strings.

```python
action Init:
  CHARSET = [0, 1]

  input = ""

atomic action Next:
  any c in CHARSET:
    input += str(c)
```

In the fizz.yaml file, you can specify the max depth we want to go.

```yaml
deadlock_detection:true
options:
  max_actions: 5
```
Note: At this moment, the online playground does not have this setting. 
You can run this on your local machine by installing from https://github.com/fizzbee-io/fizzbee/.

To run in the online playground, just set the MAX_LENGTH and an

```python
action Init:
  CHARSET = [0, 1]
  MAX_LENGTH = 5

  input = ""

atomic action Next:
  # To limit the max depth
  if len(input) > MAX_LENGTH:
    return
  any c in CHARSET:
    input += str(c)

action NoOp:
  # To avoid deadlock errors
  pass
```

Complete code:

{{% fizzbee %}}
always assertion LcsMatchNaiveLcs:
  expected = naive_lcs(input)
  actual = lcs(input)
  return actual == expected

action Init:
  CHARSET = [0, 1]
  MAX_LENGTH = 3

  input = ""


atomic action Next:
  if len(input) > MAX_LENGTH:
    return
  any c in CHARSET:
    input += str(c)

action NoOp:
  pass

atomic func lcs(b):
    n = len(b)
    f = [-1] * (2 * n)
    k = 0
    for j in range(1, 2 * n):
        if j - k >= n:
           return k
        i = f[j - k - 1]
        while b[j % n] != b[(k + i + 1) % n] and i != -1:
            if b[j % n] < b[(k + i + 1) % n]:
                k = j - i - 1
            i = f[i]
        if b[j % n] != b[(k + i + 1) % n] and i == -1:
            if b[j % n] < b[(k + i + 1) % n]:
                k = j
            f[j - k] = -1
        else:
            f[j - k] = i + 1
    return k

atomic func naive_lcs(s):
    n = len(s)
    if n == 0:
        return 0
    rotations = [s[i:] + s[:i] for i in range(n)]
    least_rotation = min(rotations)
    return rotations.index(least_rotation)

{{% /fizzbee %}}

Run the model checker, you can see the algorithm fails for the input `010`

{{% expand "Show error trace" %}}

{{< graphviz >}}
digraph G {
  "0" [label="yield
Actions: 0, Forks: 0
State: {\"CHARSET\":\"[0, 1]\",\"MAX_LENGTH\":\"3\",\"input\":\"\"\"\"}
", color="black" penwidth="2" ];
  "1" [label="Next
Actions: 1, Forks: 1
State: {\"CHARSET\":\"[0, 1]\",\"MAX_LENGTH\":\"3\",\"input\":\"\"\"\"}
Threads: 0/1
", color="black" penwidth="1" ];
  "0" -> "1" [label="Next"];
  "2" [label="yield
Actions: 1, Forks: 2
State: {\"CHARSET\":\"[0, 1]\",\"MAX_LENGTH\":\"3\",\"input\":\"\"0\"\"}
", color="black" penwidth="2" ];
  "1" -> "2" [label=""];
  "3" [label="Next
Actions: 2, Forks: 3
State: {\"CHARSET\":\"[0, 1]\",\"MAX_LENGTH\":\"3\",\"input\":\"\"0\"\"}
Threads: 0/1
", color="black" penwidth="1" ];
  "2" -> "3" [label="Next"];
  "4" [label="yield
Actions: 2, Forks: 4
State: {\"CHARSET\":\"[0, 1]\",\"MAX_LENGTH\":\"3\",\"input\":\"\"01\"\"}
", color="black" penwidth="2" ];
  "3" -> "4" [label=""];
  "5" [label="Next
Actions: 3, Forks: 5
State: {\"CHARSET\":\"[0, 1]\",\"MAX_LENGTH\":\"3\",\"input\":\"\"01\"\"}
Threads: 0/1
", color="black" penwidth="1" ];
  "4" -> "5" [label="Next"];
  "6" [label="Any:0
Actions: 3, Forks: 6
State: {\"CHARSET\":\"[0, 1]\",\"MAX_LENGTH\":\"3\",\"input\":\"\"010\"\"}
", color="red" penwidth="2" ];
  "5" -> "6" [label=""];
}

{{< /graphviz >}}

The fix proposed in the errata, change the condition.

```udiff
     f = [-1] * (2 * n)
     k = 0
     for j in range(1, 2 * n):
-        if j - k >= n:
+        if j - k > n:
            return k
         i = f[j - k - 1]
         while b[j % n] != b[(k + i + 1) % n] and i != -1:
```

{{% /expand %}}
The model checker will now pass for the input `010` but fail for `0010`.

Final solution: Remove the early return altogether.

```udiff
     f = [-1] * (2 * n)
     k = 0
     for j in range(1, 2 * n):
-        if j - k > n:
-           return k
         i = f[j - k - 1]
         while b[j % n] != b[(k + i + 1) % n] and i != -1:
             if b[j % n] < b[(k + i + 1) % n]:
```

The model checker should pass now.

As an exercise, play changing the CHARSET to [0, 1, 2] and MAX_LENGTH to 6. See how quick the state space grows.

Unlike traditional testing where you generally test for a few inputs, with formal methods, we could
test for all possible inputs.

{{< rawhtml >}}
<a href="https://imgflip.com/i/8msu16"><img src="https://i.imgflip.com/8msu16.jpg" title="made at imgflip.com" width: 360px/></a><div><a href="https://imgflip.com/memegenerator">from Imgflip Meme Generator</a></div>
{{< /rawhtml >}}

## Parting thoughts
As Andrew mentioned, pseudocode is not a good way to publish algorithms;
any executable language is better. If you compare the Python/FizzBee code with the published pseudo code, 
you'll notice they are almost the same lines of code.
With FizzBee's model checker, you can also verify the correctness of the algorithm. (At present, there is no
proof language like PlusCal/TLA+ in FizzBee.) And all this with almost negligible extra work.

As Andrew noted, simple Python worked well in this case because this algorithm
is single-threaded. However, if you're working on a concurrent or distributed algorithm,
raw Python is insufficient, but FizzBee or PlusCal would be the only option to verify correctness. 
Among these, FizzBee is orders of magnitude simpler than PlusCal/TLA+.

## References
- [Andrew Helwer's Pseudocode Showdown Python vs. PlusCal & TLA⁺](https://ahelwer.ca/post/2023-03-30-pseudocode/)
- [PlusCal and Python code](https://github.com/tlaplus/Examples/tree/master/specifications/LeastCircularSubstring)
- [A. Jesse Jiryu Davis's Pseudocode Is Not Durable](https://emptysqua.re/blog/pseudocode-is-not-durable/)
- [FizzBee](https://fizzbee.io)

