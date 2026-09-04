---
title: Symmetry Reduction
weight: 15
aliases:
  - "/tutorials/symmetry_reduction/"
description: "Symmetry reduction is a technique for modeling values and objects that are interchangeable, while reducing the number of states explored by the model checker. FizzBee supports extensive symmetry types like nominal, ordinal, interval, rotational and reflection symmetries that go beyond what are supported by most formal modeling systems."  
---

Symmetry reduction is a technique for modeling values and objects that are interchangeable, while
reducing the number of states explored by the model checker.

In many systems, the values go beyond strings and numbers, but have a more complex relationship among them.
For example UUIDs or user entered keys and values irrelevant to the system's behavior could be made interchangeable.
But if we use UUIDv7 or ULID or sometimes timestamps used for ordering, they are not completely interchangeable but has
to represent a total order. Modeling them as integers can accidentally introduce distinctions that do not exist in the system.

FizzBee provides a more extensive symmetry types that go beyond what are supported by most formal modeling systems.

Symmetry types therefore describe the relationships that are meaningful in the domain. This is useful both for accurate modeling and for reducing the state space.

{{< toc >}}

## Symmetric values

FizzBee supports 4 kinds of symmetric values.

| Type | Allowed Ops | Canonicalization | Typical Use |
|:---|:---|:---|:---|
| `nominal` | `==`, `!=` | Permutation of IDs | User IDs, UUIDv4, session tokens |
| `ordinal` | `==`, `!=`, `<`, `>`, `<=`, `>=` | Rank squashing (0, 1, 2, ...) | Logical timestamps, priorities, ordered IDs such as UUIDv7 and ULID |
| `interval` | `==`, `!=`, `<`, `>`, `<=`, `>=`, `+int`, `-int`, `val-val` | Zero-shifting (subtract min) | Sequence numbers, counters, auto-incrementing IDs |
| `rotational` | `==`, `!=`, `+int`, `-int`, `val-val` | Rotate to lex-smallest set | Ring positions, clock arithmetic |

{{% hint %}}
> **Terminology:** The names `nominal`, `ordinal`, and `interval` are borrowed from [Stevens' levels of measurement](https://en.wikipedia.org/wiki/Level_of_measurement), which classify data according to the relationships and operations that are meaningful for them. FizzBee uses these terms in a related sense to describe the structure preserved by each kind of symmetry.

{{% /hint %}}

#### Reflection symmetry

The `ordinal`, `interval`, and `rotational` symmetric values support
reflection symmetry. Reflection treats mirror-image states as equivalent,
in addition to the transformations provided by the underlying symmetry type.

The `nominal` symmetry does not need a separate reflection option because it
already treats all permutations of values as equivalent.

### Nominal symmetry

Use nominal symmetry when the values are interchangeable and only their identity
relative to other values matters, not their precise representation.

Let us say, we can have two possible keys, and two possible values, since we don't care about the actual values, we can define them as nominal symmetric values.

The possible states are:

| Length | Equivalent States                          | Canonical State         | Comment              |
|--------|-------------------------------------------|-------------------------|----------------------|
| 0      | {}                                        | {}                      | No keys or values    |
| 1      | {k0:v0}, {k0:v1}, {k1:v0}, {k1:v1}        | {k0:v0}                | One key, one value   |
| 2      | {k0:v0, k1:v0}, {k0:v1, k1:v1}            | {k0:v0, k1:v0}         | Two keys, same value |
| 2      | {k0:v0, k1:v1}, {k0:v1, k1:v0}            | {k0:v0, k1:v1}         | Two keys, different values |

{{% hint type=note %}}
**Mathematical terminology:** Nominal symmetry corresponds to the action of
the **symmetric group** S<sub>n</sub>, which contains all permutations of the `n` values.
{{% /hint %}}

#### fresh() creates a new canonical value
{{% fizzbee %}}
KEYS = symmetry.nominal("k", 2)
VALUES = symmetry.nominal("v", 3)

action Init:
  data = {}

atomic action Put:
  k = KEYS.fresh()
  v = VALUES.fresh()
  data[k] = v

{{% /fizzbee %}}

When you run it, you'll see a deadlock error because after creating 2 new keys, Put cannot proceed because the fresh()
would disable the action, as the number of keys is limited to 2. Before we fix it, open the states graph.

{{% graphviz %}}
digraph G {
"0x79f4121b6000" [label="yield
Actions: 0, Forks: 0
State: {\"data\":{}}
", color="black" penwidth="2" ];
"0x79f4121b6000" -> "0x79f4121b6080" [label="Put", color="black" penwidth="1" ];
"0x79f4121b6080" [label="yield
Actions: 1, Forks: 1
State: {\"data\":{\"k0\":\"v0\"}}
", color="black" penwidth="2" ];
"0x79f4121b6080" -> "0x79f4121b6280" [label="Put", color="black" penwidth="1" ];
"0x79f4121b6280" [label="yield
Actions: 2, Forks: 2
State: {\"data\":{\"k0\":\"v0\",\"k1\":\"v1\"}}
", color="black" penwidth="2" ];
}

{{% /graphviz %}}

So, each Put action instantiated a new key and a new value, and after 2 keys are created, no further action was possible.

To skip the error, you could disable deadlock detection adding this snippet at the top.
```python
---
deadlock_detection: false
---
```

#### values() returns the list of active values
{{% fizzbee %}}
KEYS = symmetry.nominal("k", 2)
VALUES = symmetry.nominal("v", 3)

action Init:
  data = {}

atomic action Put:
  k = KEYS.fresh()
  v = VALUES.fresh()
  data[k] = v

atomic action Delete:
  k = oneof KEYS.values()
  data.pop(k)

{{% /fizzbee %}}

When you run it in the playground, you'll see 3 unique states and the state graph looks like this.
(But the two arrows colored blue and red for attention)
{{% graphviz %}}
digraph G {
"0x6e6755534000" [label="yield
Actions: 0, Forks: 0
State: {\"data\":{}}
", color="black" penwidth="2" ];
"0x6e6755534000" -> "0x6e6755534080" [label="Put", color="black" penwidth="1" ];
"0x6e6755534080" [label="yield
Actions: 1, Forks: 1
State: {\"data\":{\"k0\":\"v0\"}}
", color="black" penwidth="2" ];
"0x6e6755534080" -> "0x6e6755534380" [label="Put", color="black" penwidth="1" ];
"0x6e6755534380" [label="yield
Actions: 2, Forks: 2
State: {\"data\":{\"k0\":\"v0\",\"k1\":\"v1\"}}
", color="black" penwidth="2" ];
"0x6e6755534380" -> "0x6e6755534700" [label="Delete", color="black" penwidth="1" ];
"0x6e6755534700" [label="Delete
Actions: 3, Forks: 3
State: {\"data\":{\"k0\":\"v0\",\"k1\":\"v1\"}}
Threads: 0/1
", color="black" penwidth="1" ];
"0x6e6755534700" -> "0x6e6755534080" [label="Any:k=k0", color="red" penwidth="1" ];
"0x6e6755534700" -> "0x6e6755534080" [label="Any:k=k1", color="blue" penwidth="1" ];
"0x6e6755534080" -> "0x6e6755534480" [label="Delete", color="black" penwidth="1" ];
"0x6e6755534480" [label="Delete
Actions: 2, Forks: 2
State: {\"data\":{\"k0\":\"v0\"}}
Threads: 0/1
", color="black" penwidth="1" ];
"0x6e6755534480" -> "0x6e6755534000" [label="Any:k=k0", color="black" penwidth="1" ];
}

{{% /graphviz %}}

**Blue arrow:**
From {k0:v0, k1:v1} when you delete the key k1, it becomes {k0:v0}. This is obvious.

**Red arrow:**
From {k0:v0, k1:v1} when you delete the key k0, it becomes {k1:v1}. But the model checker canonicalizes it to {k0:v0} because the keys are symmetric. 
This is symmetry reduction.

#### choices() returns the list of active values plus one fresh value
Previously, we made Put to always insert a new key and a new value. But often we want to say overwrite a key with a new value,
or multiple keys can have same values. We could do it by combining the `values()` and `fresh()` methods, but that is
non trivial to get it to work because if the state already has 2 entries, then `fresh()` will be disabled and the action will not be possible.

So FizzBee provides a convenient method called `choices()` that returns the list of active values plus one fresh value.

{{% fizzbee %}}
KEYS = symmetry.nominal("k", 2)
VALUES = symmetry.nominal("v", 3)

action Init:
  data = {}

atomic action Put:
  k = oneof KEYS.choices()
  v = oneof VALUES.choices()
  data[k] = v

# Lets remove the Delete method to keep the state graph small enough to follow
{{% /fizzbee %}}

Trace through the generated state graph to see how the various states are canonicalized.

### Ordinal symmetry

Use ordinal symmetry when the values are interchangeable, but their relative order matters. Unlike nominal symmetry, the model checker preserves comparisons such as a < b, while ignoring the absolute values assigned to a and b.
For example, logical timestamps, priorities, or ordered IDs such as UUIDv7 and ULID.

{{% fizzbee %}}

TIMES = symmetry.ordinal(name="ts", limit=4)

action Init:
    events = []

atomic action RecordEvent:
    # fresh() appends after max; min()/max() return the extremes.
    t = TIMES.fresh()
    events = events + [t]

atomic action ProcessEvent:
    # Consuming the oldest event frees a slot, allowing fresh()
    # to allocate again -- enabling infinite traces without deadlock.
    require len(events) > 0
    events = events[1:]

always assertion EventsOrdered:
    # The application requires events to remain ordered.
    for i in range(len(events) - 1):
        if not (events[i] < events[i + 1]):
            return False
    return True

{{% /fizzbee %}}

{{% hint type=note %}}
**Mathematical terminology:** Ordinal symmetry preserves the total ordering of
the values. Its transformations are order-preserving relabelings of the
ordered domain.
{{% /hint %}}

#### Ordinal Segments (Gap Insertion)

`segments()` returns gap objects between active values. Each gap has a `fresh()` method to allocate a value within that range.

```python
TIMES = symmetry.ordinal(name="ts", limit=6)

action Init:
    t_start = TIMES.fresh()
    t_end = TIMES.fresh()

atomic action InsertBetween:
    # segments(after=v, before=v) filters to gaps in range.
    # Ordinal gaps are always non-empty (the domain is dense).
    gaps = TIMES.segments(after=t_start, before=t_end)
    gap = oneof gaps
    t = gap.fresh()  # guaranteed: t_start < t < t_end
```

With N active values, `segments()` returns N+1 gaps: a head gap (before first), body gaps (between consecutive pairs), and a tail gap (after last). Ordinal gaps are always non-empty since the domain is dense (infinitely divisible in theory).

### Interval Symmetry

Use interval symmetry when values have a meaningful order and differences between values are meaningful. Unlike ordinal symmetry, the distance between values is preserved.

Supports arithmetic on values. The model checker normalizes by subtracting the minimum (zero-shifting), so `{5,7,8}` and `{0,2,3}` are equivalent.

```python
TICKS = symmetry.interval(name="v", limit=6)

action Init:
    t1 = TICKS.min()
    t2 = TICKS.min()   # same value as t1

atomic fair action Tick1:
    t1 = t1 + 1        # val + int -> val

atomic fair action Tick2:
    t2 = t2 + 1
```
When you run this and open the graph, it will look like this. One arrow highlighted with red here.

{{% graphviz %}}
digraph G {
  "0x5eadeaab4000" [label="yield
Actions: 0, Forks: 0
State: {\"t1\":\"v0\",\"t2\":\"v0\"}
", color="black" penwidth="2" ];
  "0x5eadeaab4000" -> "0x5eadeaab4180" [label="Tick1", color="forestgreen" penwidth="1" ];
  "0x5eadeaab4180" [label="yield
Actions: 1, Forks: 1
State: {\"t1\":\"v1\",\"t2\":\"v0\"}
", color="black" penwidth="2" ];
  "0x5eadeaab4180" -> "0x5eadeaab4480" [label="Tick1", color="forestgreen" penwidth="1" ];
  "0x5eadeaab4480" [label="yield
Actions: 2, Forks: 2
State: {\"t1\":\"v2\",\"t2\":\"v0\"}
", color="black" penwidth="2" ];
  "0x5eadeaab4480" -> "0x5eadeaab4a80" [label="Tick1", color="forestgreen" penwidth="1" ];
  "0x5eadeaab4a80" [label="yield
Actions: 3, Forks: 3
State: {\"t1\":\"v3\",\"t2\":\"v0\"}
", color="black" penwidth="2" ];
  "0x5eadeaab4a80" -> "0x5eadeaab5280" [label="Tick1", color="forestgreen" penwidth="1" ];
  "0x5eadeaab5280" [label="yield
Actions: 4, Forks: 4
State: {\"t1\":\"v4\",\"t2\":\"v0\"}
", color="black" penwidth="2" ];
  "0x5eadeaab5280" -> "0x5eadeaab5a80" [label="Tick1", color="forestgreen" penwidth="1" ];
  "0x5eadeaab5a80" [label="yield
Actions: 5, Forks: 5
State: {\"t1\":\"v5\",\"t2\":\"v0\"}
", color="black" penwidth="2" ];
  "0x5eadeaab5a80" -> "0x5eadeaab5280" [label="Tick2", color="red" penwidth="2" ];
  "0x5eadeaab5280" -> "0x5eadeaab4a80" [label="Tick2", color="forestgreen" penwidth="1" ];
  "0x5eadeaab4a80" -> "0x5eadeaab4480" [label="Tick2", color="forestgreen" penwidth="1" ];
  "0x5eadeaab4480" -> "0x5eadeaab4180" [label="Tick2", color="forestgreen" penwidth="1" ];
  "0x5eadeaab4180" -> "0x5eadeaab4000" [label="Tick2", color="forestgreen" penwidth="1" ];
  "0x5eadeaab4000" -> "0x5eadeaab4280" [label="Tick2", color="forestgreen" penwidth="1" ];
  "0x5eadeaab4280" [label="yield
Actions: 1, Forks: 1
State: {\"t1\":\"v0\",\"t2\":\"v1\"}
", color="black" penwidth="2" ];
  "0x5eadeaab4280" -> "0x5eadeaab4000" [label="Tick1", color="forestgreen" penwidth="1" ];
  "0x5eadeaab4280" -> "0x5eadeaab4880" [label="Tick2", color="forestgreen" penwidth="1" ];
  "0x5eadeaab4880" [label="yield
Actions: 2, Forks: 2
State: {\"t1\":\"v0\",\"t2\":\"v2\"}
", color="black" penwidth="2" ];
  "0x5eadeaab4880" -> "0x5eadeaab4280" [label="Tick1", color="forestgreen" penwidth="1" ];
  "0x5eadeaab4880" -> "0x5eadeaab5080" [label="Tick2", color="forestgreen" penwidth="1" ];
  "0x5eadeaab5080" [label="yield
Actions: 3, Forks: 3
State: {\"t1\":\"v0\",\"t2\":\"v3\"}
", color="black" penwidth="2" ];
  "0x5eadeaab5080" -> "0x5eadeaab4880" [label="Tick1", color="forestgreen" penwidth="1" ];
  "0x5eadeaab5080" -> "0x5eadeaab5880" [label="Tick2", color="forestgreen" penwidth="1" ];
  "0x5eadeaab5880" [label="yield
Actions: 4, Forks: 4
State: {\"t1\":\"v0\",\"t2\":\"v4\"}
", color="black" penwidth="2" ];
  "0x5eadeaab5880" -> "0x5eadeaab5080" [label="Tick1", color="forestgreen" penwidth="1" ];
  "0x5eadeaab5880" -> "0x5eadeab80180" [label="Tick2", color="forestgreen" penwidth="1" ];
  "0x5eadeab80180" [label="yield
Actions: 5, Forks: 5
State: {\"t1\":\"v0\",\"t2\":\"v5\"}
", color="black" penwidth="2" ];
  "0x5eadeab80180" -> "0x5eadeaab5880" [label="Tick1", color="blue" penwidth="2" ];
}

{{% /graphviz %}}

Focus on the red arrow. It is from the state {t1=v5, t2=v0}. On Tick2, the state becomes {t1=v5, t2=v1}. The {t1=v5, t2=v1} is then cannonicalized to {t1=v4, t2=v1}. That is, it still preserved the distance between t1 and t2.
Similarly, the blue arrow shows, {t1=v0, t2=v5} on Tick1 becomes {t1=v1, t2=v5} and is cannonicalized to {t1=v0, t2=v4}. The distance between t1 and t2 is preserved.

**Arithmetic**: `val + int` and `val - int` produce new symmetric values. `val1 - val2` produces a plain `int` (the distance). Only the gap pattern matters -- the model checker recognizes that `{t1=0,t2=3}` is equivalent to `{t1=100,t2=103}`.

With ordinal symmetry, {5, 10} and {0, 1} are equivalent because they have the same ordering. With interval symmetry, {5, 10} and {0, 1} are not equivalent because their distances differ. {5, 10} and {100, 105} are equivalent because both have distance 5.

{{% hint type=note %}}
**Mathematical terminology:** Interval symmetry is based on translation
symmetry: shifting every value by the same amount preserves all pairwise
differences.
{{% /hint %}}


#### Divergence (Bounding Spread)

The `divergence` parameter limits `max - min` across all active values. Transitions that would exceed this bound are pruned from the state space.

```python
# max spread of 3: states where (max - min) > 3 are unreachable
SEQ = symmetry.interval(name="s", divergence=3)

action Init:
    head = SEQ.fresh()     # s0
    tail = SEQ.fresh()     # s1

atomic fair action AdvanceHead:
    head = head + 1        # pruned if head - tail > 3

atomic fair action AdvanceTail:
    require tail < head
    tail = tail + 1
```

### Rotational symmetry

Values are integers mod `limit` (ring positions). Arithmetic wraps around. No ordering operators (`<`, `>` not supported) since the domain is circular.

```python
RING = symmetry.rotational(name="pos", limit=5)

action Init:
    positions = set()

atomic action Place:
    p = RING.fresh()
    positions.add(p)

atomic action Advance:
    p = oneof positions
    next_p = p + 1          # wraps: 4 + 1 = 0 on ring of 5
    if next_p not in positions:
        positions.remove(p)
        positions.add(next_p)
```

The model checker rotates all values by a constant to find the lexicographically smallest set. So `{0,2}`, `{1,3}`, `{2,4}`, `{3,0}`, `{4,1}` are all the same state (gap pattern = {0,2}).

`val1 - val2` returns a plain `int`: `(a - b) % limit`.
{{% hint type=note %}}
**Mathematical terminology:** Rotational symmetry treats cyclic rotations of
the domain as equivalent. These transformations form a cyclic group C<sub>n</sub>.
When combined with reflection symmetry, the transformations form a dihedral group D<sub>n</sub>.
{{% /hint %}}


### API Reference
#### Constructors

```python
symmetry.nominal(name, limit, materialize=False)
symmetry.ordinal(name, limit, reflection=False, materialize=False)
symmetry.interval(name, divergence=None, limit=None, start=0, reflection=False, materialize=False)
symmetry.rotational(name, limit, materialize=False, reflection=False)
```

**Parameters**:
- `name` (string): Domain identifier, used in value display (e.g., name="ts" produces ts0, ts1, ...)
- `limit` (int): Maximum number of values in the domain
- `divergence` (int, interval only): Maximum allowed spread (max - min). If only `divergence` given, `limit = divergence + 1`. If only `limit` given, `divergence = limit - 1`.
- `start` (int, interval only): Starting value for first allocation (default 0)
- `reflection` (bool): Enable mirror-state equivalence (not available for nominal)
- `materialize` (bool): Pre-populate all `limit` values at declaration time. When true, `fresh()` is disallowed.

#### Methods by Type

| Method | Nominal | Ordinal | Interval | Rotational | Description |
|:---|:---:|:---:|:---:|:---:|:---|
| `fresh()` | Y | Y | Y | Y | Allocate new canonical value |
| `values()` | Y | Y | Y | Y | List active values (sorted) |
| `choose()` | Y | - | - | Y | Deterministic default value (like TLA+ CHOOSE) |
| `choices()` | Y | - | - | Y | `values()` + one `fresh()` |
| `min()` | - | Y | Y | - | Smallest active value or fresh |
| `max()` | - | Y | Y | - | Largest active value or fresh |
| `segments(after?, before?)` | - | Y | - | - | Gaps between active values |

### Migrating from symmetric_values()

Sometimes you would want a simple value for the ID or Key.
Instead of defining the keys as strings or numbers, 
you can define them as `symmetric_values`.

{{% fizzbee %}}
# Define the keys as symmetric values instead of strings or numbers
KEYS = symmetric_values('k', 3)  # instead of KEYS = range(0, 3)

action Init:
  switches = {}
  for k in KEYS:
      switches[k] = 'OFF'
  

atomic action On:
  any k in KEYS:
    switches[k] = 'ON'

{{% /fizzbee %}}

The precise equivalent of it in the new API is `KEYS = symmetry.nominal("k", 3, materialize=True)`.
Make these changes.
```udiff
@@ -1,11 +1,11 @@
-KEYS = symmetric_values('k', 3)  # instead of KEYS = range(0, 3)
+KEYS = symmetry.nominal("k", 3, materialize=True)
 
 action Init:
   switches = {}
-  for k in KEYS:
+  for k in KEYS.values():
       switches[k] = 'OFF'
   
 
 atomic action On:
-  oneof k in KEYS:
-    switches[k] = 'ON'
+  k = oneof KEYS.values()
+  switches[k] = 'ON'
```

{{% fizzbee %}}
KEYS = symmetry.nominal("k", 3, materialize=True)

action Init:
  switches = {}
  for k in KEYS.values():
      switches[k] = 'OFF'
  

atomic action On:
  k = oneof KEYS.values()
  switches[k] = 'ON'
{{% /fizzbee %}}

## Symmetric Roles
Symmetric roles are useful when you have multiple instances of the same role and 
their identities are interchangeable. FizzBee can then avoid exploring states that 
differ only by a permutation of those role instances.

{{% fizzbee %}}
Status = enum('INIT', 'DONE')

NUM_ROLES = 5

symmetric role Node:

  action Init:
    self.status = Status.INIT

  atomic action Done:
    self.status = Status.DONE
    done.add(self.__id__)

action Init:
  nodes = bag()
  for i in range(0, NUM_ROLES):
    nodes.add(Node())
  done = set()
{{% /fizzbee %}}

You can try it by removing the `symmetric` keyword
and see the difference in the number of states generated.

{{% hint type=warning %}}
At present, the new API does not support symmetric roles with ordinal, interval, or rotational symmetry. 
Only nominal symmetry is supported.
Let us when you want to use symmetric roles with other symmetry types as well, on our discord channel or raise a github issue.
{{% /hint %}}

## Order independent data structures
To reduce states explored, remember to use bags when possible instead of lists.
This will ensure, the order of operations are not relevant.
For more information on the available data structures, see the [Data structures](/tutorials/datastructures) tutorial.

## Assertions and Symmetry
When you use assertions, remember that the assertion is checked before canonicalization. 
While generally this is irrelevant for most assertions, for some assertions like the `transition` assertion, 
it is important and useful. 

For example:
{{% fizzbee %}}
NUMBERS = symmetry.interval("n", 3)

action Init:
  value = NUMBERS.min()  

atomic action Inc:
  value += 1

transition assertion Monotonic(before, after):
  return before.value <= after.value

transition assertion MaxDiff(before, after):
  return after.value - before.value == 1

{{% /fizzbee %}}

When you run it, it will only show a single state. Since the transition assertion is checked before the canonicalization,
the assertion passes as the after.value is still 1.
```
Model checking BuzzyMcBee.json
configFileName: fizz.yaml
StateSpaceOptions: options:{max_actions:100 max_concurrent_actions:2 crash_on_yield:true} liveness:"strict" deadlock_detection:true
Nodes: 1, queued: 0, elapsed: 198.125µs
Time taken for model checking: 202.25µs
Valid Nodes: 1 Unique states: 1
IsLive: true
Time taken to check liveness: 92µs
PASSED: Model checker completed successfully
```


{{% graphviz %}}
digraph G {
  "0x5ce8f58a4000" [label="yield
Actions: 0, Forks: 0
State: {\"value\":\"n0\"}
", color="black" penwidth="2" ];
  "0x5ce8f58a4000" -> "0x5ce8f58a4000" [label="Inc", color="black" penwidth="1" ];
}

{{% /graphviz %}}

Now, change the assertion,
```udiff
@@ -12,2 +12,2 @@
 transition assertion MaxDiff(before, after):
-  return after.value - before.value == 1
+  return after.value - before.value == 0
```
When you run it, you will see this error.
```
Model checking BuzzyMcBee.json
configFileName: fizz.yaml
StateSpaceOptions: options:{max_actions:100 max_concurrent_actions:2 crash_on_yield:true} liveness:"strict" deadlock_detection:true
Nodes: 1, queued: 0, elapsed: 958.209µs
Time taken for model checking: 965.666µs
FAILED: Model checker failed. Transition Invariant: MaxDiff
------
Init
--
state: {"value":"n0"}
------
Inc
--
state: {"value":"n1"}
------
```
with this state graph

{{% graphviz %}}
digraph G {
"0x9967fb06000" [label="yield
Actions: 0, Forks: 0
State: {\"value\":\"n0\"}
", color="black" penwidth="2" ];
"0x9967fb06000" -> "0x9967fb06100" [label="Inc", color="red" penwidth="1" ];
"0x9967fb06100" [label="yield
Actions: 1, Forks: 1
State: {\"value\":\"n1\"}
", color="black" penwidth="2" ];
}

{{% /graphviz %}}

## Choosing the right symmetry type
| If your values...                             | Use          |
| --------------------------------------------- | ------------ |
| Are interchangeable and only equality matters | `nominal`    |
| Have an order, but not meaningful distances   | `ordinal`    |
| Have meaningful order and distances           | `interval`   |
| Represent positions on a cycle                | `rotational` |

Choose the weakest symmetry that preserves all relationships relevant to your model.
