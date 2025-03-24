---
title: Performance Modeling
description: "Go beyond correctness—model system performance in FizzBee. Analyze response latency, throughput, error rates, resource utilization, and scalability using probabilistic techniques."
weight: 30
---

When designing any system, besides evaluating the behavioral properties like
will the system become consistent and produce correct results, the other key
aspect to consider is the performance of the system. For example, 
- Response latency: Mean and tail latencies
- Error rates
- Throughput: How many requests can the system handle per second
- Resource utilization
- Cost
- Scalability
and so on.

We will see how to model these in FizzBee.

This article assumes, you have gone through [Probabilistic modeling](/tutorials/probabilistic-modeling).
We will use the same examples probabilistic modeling and add performance characteristics to it. 

{{< toc >}}

## Basics
The performance metrics are called `counters` in FizzBee.

{{% hint %}}
In the literature or 
in other tools like PRISM, usually the two terms used are either `cost` or `reward`.
Unfortunately, they have either positive or negative meaning. So, we chose to use `counter`.

That way, `latency` is not called a `reward`.
{{% /hint %}}

Let us start with the naivest example as in the probabilistic modeling - a single coin toss.

Create a folder for this example. Let's call it `simple_coin`.

`samples/simple-coin/CoinToss.fizz`:
```python
action Toss:
  oneof:
    `head` return "head"
    `tail` return "tail"
```

Since we just want to limit to a single coin toss, the easiest way to do is, say that in fizz.yaml file.

`samples/simple-coin/fizz.yaml`:
```yaml
options:
  maxActions: 1

```
As we saw before, both has equal probability of 0.5 by default, that can be changed as needed. 

Now, lets define te performance model config.
Here, you have a counter called `points` that is numeric (int or float).

`samples/simple-coin/perf_model.yaml`:
```yaml
configs:
  Toss.head:
    probability: 0.5
    counters:
      points:
        numeric: 2
  Toss.tail:
    probability: 0.5
    counters:
      points:
        numeric: 1


```
Now, run the model checker as usual, and then run the performance model checker as well.

```bash
./fizz samples/simple-coin/CoinToss.fizz
Model checking samples/simple-coin/CoinToss.json
configFileName: samples/simple-coin/fizz.yaml
StateSpaceOptions: options:{max_actions:1 max_concurrent_actions:1}
Nodes: 4, elapsed: 80.416µs
Time taken for model checking: 85.792µs
Writen graph dotfile: samples/simple-coin/out/run_2024-05-08_22-19-26/graph.dot
To generate svg, run: 
dot -Tsvg samples/simple-coin/out/run_2024-05-08_22-19-26/graph.dot -o graph.svg && open graph.svg
Max Depth 2
PASSED: Model checker completed successfully
Writen 1 node files and 1 link files to dir samples/simple-coin/out/run_2024-05-08_22-19-26
```
Use this, to run the performance model checker.

```bash
bazel-bin/performance/performance_bin \
    --states samples/simple-coin/out/run_2024-05-08_22-19-26/  \
    --source samples/simple-coin/CoinToss.json \
    --perf samples/simple-coin/perf_model.yaml

Metrics(mean={'points': 1.5}, histogram=[(1.0, {'points': 1.5})])
   2: 0.50000000 state: {} / returns: {"Toss":"\"head\""}
   3: 0.50000000 state: {} / returns: {"Toss":"\"tail\""}
```
It will also show a graph, but that is not very interesting for this case.

Here, it says that the mean points is 1.5. That is because, the head gives 2 points and tail gives 1 point, with equal probability.
So, the mean is 1.5.

Let us, change the probability to, say, 0.8 and 0.2.

```
Metrics(mean={'points': 1.2000000000000002}, histogram=[(1.0, {'points': 1.2000000000000002})])
   2: 0.20000000 state: {} / returns: {"Toss":"\"head\""}
   3: 0.80000000 state: {} / returns: {"Toss":"\"tail\""}

```
That is, expected number of points is 1.2. (0.2 * 2 + 0.8 * 1)

## Simulating a 6-sided die with a fair coin
Using the same example from the [probabilistic modeling](/tutorials/probabilistic-modeling/#simulating-a-6-sided-die-with-a-fair-coin),
let us see how to add performance metrics to it.

Use the same code, but add the `perf_model.yaml` file.

`samples/die/perf_model.yaml`:
```yaml
configs:
  Toss.head:
    counters:
      toss:
        numeric: 1
  Toss.tail:
    counters:
      toss:
        numeric: 1

```
Now, run the performance model checker.

```bash
bazel-bin/performance/performance_bin \
    --states samples/die/out/run_2024-05-08_22-34-14/  \
    --source samples/die/Die.json \
    --perf samples/die/perf_model.yaml
Metrics(mean={'toss': 3.666666666665151}, histogram=[(0.75, {'toss': 3.0}), (0.9375, {'toss': 5.0}), (0.984375, {'toss': 7.0}), (0.99609375, {'toss': 9.0}), (0.9990234375, {'toss': 11.0}), (0.999755859375, {'toss': 13.0}), (0.99993896484375, {'toss': 15.0}), (0.9999847412109375, {'toss': 17.0}), (0.9999961853027344, {'toss': 19.0}), (0.9999990463256836, {'toss': 21.0}), (0.9999997615814209, {'toss': 23.0}), (0.9999999403953552, {'toss': 25.0}), (0.9999999850988388, {'toss': 27.0}), (0.9999999962747097, {'toss': 29.0}), (0.9999999990686774, {'toss': 31.0}), (0.9999999997671694, {'toss': 33.0}), (0.9999999999417923, {'toss': 35.0}), (0.9999999999854481, {'toss': 37.0}), (0.999999999996362, {'toss': 39.0}), (0.9999999999990905, {'toss': 41.0})])
   8: 0.16666667 state: {} / returns: {"Roll":"1"}
   9: 0.16666667 state: {} / returns: {"Roll":"2"}
  10: 0.16666667 state: {} / returns: {"Roll":"3"}
  11: 0.16666667 state: {} / returns: {"Roll":"4"}
  12: 0.16666667 state: {} / returns: {"Roll":"5"}
  13: 0.16666667 state: {} / returns: {"Roll":"6"}
```

As before, we see the termination probabilities for each state - confirms 
the die is fair. But what is new here is, the distribution.

The mean toss is 3.67. That is, on average, you will need 3.67 coin tosses to simulate a 6-sided die.
It also has the histogram. The minimum number of tosses required 3 that happens 75% of the time.
Then, 5 tosses 93.75% of the time, and so on.
It takes 11 tosses to respond to 99.9% of the time.

### Change the algorithm to see the impact on the performance
As we tried previously, let us make a tiny change. Instead of repeating the last 2 tosses when we 0 or 7,
what if we repeated all three tosses.

```udiff
@@ -5,8 +5,9 @@
 
 atomic action Roll:
-  toss0 = Toss()
+
   while True:
+    toss0 = Toss()
     toss1 = Toss()
     toss2 = Toss()
```

```bash
Metrics(mean={'toss': 3.999999999998181}, histogram=[(0.75, {'toss': 3.0}), (0.9375, {'toss': 6.0}), (0.984375, {'toss': 9.0}), (0.99609375, {'toss': 12.0}), (0.9990234375, {'toss': 15.0}), (0.999755859375, {'toss': 18.0}), (0.99993896484375, {'toss': 21.0}), (0.9999847412109375, {'toss': 24.0}), (0.9999961853027344, {'toss': 27.0}), (0.9999990463256836, {'toss': 30.0}), (0.9999997615814209, {'toss': 33.0}), (0.9999999403953552, {'toss': 36.0}), (0.9999999850988388, {'toss': 39.0}), (0.9999999962747097, {'toss': 42.0}), (0.9999999990686774, {'toss': 45.0}), (0.9999999997671694, {'toss': 48.0}), (0.9999999999417923, {'toss': 51.0}), (0.9999999999854481, {'toss': 54.0}), (0.999999999996362, {'toss': 57.0}), (0.9999999999990905, {'toss': 60.0})])
   8: 0.16666667 state: {} / returns: {"Roll":"1"}
   9: 0.16666667 state: {} / returns: {"Roll":"2"}
  10: 0.16666667 state: {} / returns: {"Roll":"3"}
  11: 0.16666667 state: {} / returns: {"Roll":"4"}
  12: 0.16666667 state: {} / returns: {"Roll":"5"}
  13: 0.16666667 state: {} / returns: {"Roll":"6"}
```

The result will still produce 1-6 with equal probability. Although this change,
results in the fair die, but the performance characteristics is slightly different.

Now, it takes a mean of 4 coin tosses to simulate a 6-sided die instead of just 3.66.
On the histogram, you can see that, 75% of the time, it still takes only 3 tosses.
but the tail is getting longer with 15 tosses to reach 99.9%.

## Simulating a fair coin from an unfair coin
Use the example from the [probabilistic modeling](/tutorials/probabilistic-modeling/#simulating-a-fair-coin-with-a-biased-coin),

Find the average number of tosses required to simulate a fair coin, and get the histogram
1. With a fair die
2. With a biased die (head: 0.9, tail: 0.1)

Try this as an exercise. The `samples/fair-coin/FairCoin.fizz` and `fizz.yaml` are the same.
You just need to define the counters in the `perf_model_unbiased.yaml` and `perf_model_biased.yaml` files.

{{% expand "Show solution" %}}

*Unbiased*
`samples/fair-coin/perf_model_unbiased.yaml`:
```yaml
configs:
  UnfairToss.head:
    probability: 0.5
    counters:
      toss:
        numeric: 1
  UnfairToss.tail:
    probability: 0.5
    counters:
      toss:
        numeric: 1
```
```bash
Metrics(mean={'toss': 3.999999999998181}, histogram=[(0.5, {'toss': 2.0}), (0.75, {'toss': 4.0}), (0.875, {'toss': 6.0}), (0.9375, {'toss': 8.0}), (0.96875, {'toss': 10.0}), (0.984375, {'toss': 12.0}), (0.9921875, {'toss': 14.0}), (0.99609375, {'toss': 16.0}), (0.998046875, {'toss': 18.0}), (0.9990234375, {'toss': 20.0}), (0.99951171875, {'toss': 22.0}), (0.999755859375, {'toss': 24.0}), (0.9998779296875, {'toss': 26.0}), (0.99993896484375, {'toss': 28.0}), (0.999969482421875, {'toss': 30.0}), (0.9999847412109375, {'toss': 32.0}), (0.9999923706054688, {'toss': 34.0}), (0.9999961853027344, {'toss': 36.0}), (0.9999980926513672, {'toss': 38.0}), (0.9999990463256836, {'toss': 40.0}), (0.9999995231628418, {'toss': 42.0}), (0.9999997615814209, {'toss': 44.0}), (0.9999998807907104, {'toss': 46.0}), (0.9999999403953552, {'toss': 48.0}), (0.9999999701976776, {'toss': 50.0}), (0.9999999850988388, {'toss': 52.0}), (0.9999999925494194, {'toss': 54.0}), (0.9999999962747097, {'toss': 56.0}), (0.9999999981373549, {'toss': 58.0}), (0.9999999990686774, {'toss': 60.0}), (0.9999999995343387, {'toss': 62.0}), (0.9999999997671694, {'toss': 64.0}), (0.9999999998835847, {'toss': 66.0}), (0.9999999999417923, {'toss': 68.0}), (0.9999999999708962, {'toss': 70.0}), (0.9999999999854481, {'toss': 72.0}), (0.999999999992724, {'toss': 74.0}), (0.999999999996362, {'toss': 76.0}), (0.999999999998181, {'toss': 78.0}), (0.9999999999990905, {'toss': 80.0}), (0.9999999999995453, {'toss': 82.0})])
   4: 0.50000000 state: {} / returns: {"FairToss":"\"head\""}
   5: 0.50000000 state: {} / returns: {"FairToss":"\"tail\""}
```

*Biased*
`samples/fair-coin/perf_model_biased.yaml`:
```yaml
configs:
  UnfairToss.head:
    probability: 0.9
    counters:
      toss:
        numeric: 1
  UnfairToss.tail:
    probability: 0.1
    counters:
      toss:
        numeric: 1
```

```bash
Metrics(mean={'toss': 11.111111111103344}, histogram=[(0.18000000000000002, {'toss': 2.0}), (0.3276, {'toss': 4.0}), (0.44863200000000003, {'toss': 6.0}), (0.5478782400000001, {'toss': 8.0}), (0.6292601568, {'toss': 10.0}), (0.695993328576, {'toss': 12.0}), (0.7507145294323201, {'toss': 14.0}), (0.7955859141345024, {'toss': 16.0}), (0.832380449590292, {'toss': 18.0}), (0.8625519686640395, {'toss': 20.0}), (0.8872926143045123, {'toss': 22.0}), (0.9075799437297002, {'toss': 24.0}), (0.924215553858354, {'toss': 26.0}), (0.9378567541638503, {'toss': 28.0}), (0.9490425384143573, {'toss': 30.0}), (0.958214881499773, {'toss': 32.0}), (0.9657362028298139, {'toss': 34.0}), (0.9719036863204474, {'toss': 36.0}), (0.9769610227827669, {'toss': 38.0}), (0.9811080386818688, {'toss': 40.0}), (0.9845085917191324, {'toss': 42.0}), (0.9872970452096885, {'toss': 44.0}), (0.9895835770719447, {'toss': 46.0}), (0.9914585331989947, {'toss': 48.0}), (0.9929959972231757, {'toss': 50.0}), (0.9942567177230041, {'toss': 52.0}), (0.9952905085328634, {'toss': 54.0}), (0.996138216996948, {'toss': 56.0}), (0.9968333379374972, {'toss': 58.0}), (0.9968333379374973, {'toss': 59.0}), (0.9974033371087477, {'toss': 60.0}), (0.9978707364291731, {'toss': 62.0}), (0.998254003871922, {'toss': 64.0}), (0.998568283174976, {'toss': 66.0}), (0.9988259922034803, {'toss': 68.0}), (0.9990373136068539, {'toss': 70.0}), (0.9992105971576202, {'toss': 72.0}), (0.9993526896692485, {'toss': 74.0}), (0.9994692055287838, {'toss': 76.0}), (0.9995647485336028, {'toss': 78.0}), (0.9996430937975543, {'toss': 80.0}), (0.9997073369139946, {'toss': 82.0}), (0.9997600162694756, {'toss': 84.0}), (0.9998032133409698, {'toss': 86.0}), (0.9998032133409699, {'toss': 87.0}), (0.9998386349395953, {'toss': 88.0}), (0.9998676806504682, {'toss': 90.0}), (0.9998914981333838, {'toss': 92.0}), (0.9999110284693747, {'toss': 94.0}), (0.9999270433448872, {'toss': 96.0}), (0.9999270433448874, {'toss': 97.0}), (0.9999401755428077, {'toss': 98.0}), (0.9999509439451023, {'toss': 100.0}), (0.9999597740349839, {'toss': 102.0}), (0.9999670147086869, {'toss': 104.0}), (0.999972952061123, {'toss': 106.0}), (0.9999778206901209, {'toss': 108.0}), (0.999977820690121, {'toss': 109.0}), (0.9999818129658992, {'toss': 110.0}), (0.9999850866320373, {'toss': 112.0}), (0.9999877710382706, {'toss': 114.0}), (0.999989972251382, {'toss': 116.0}), (0.9999917772461332, {'toss': 118.0}), (0.9999932573418292, {'toss': 120.0}), (0.9999944710202999, {'toss': 122.0}), (0.9999954662366459, {'toss': 124.0}), (0.9999962823140497, {'toss': 126.0}), (0.9999969514975208, {'toss': 128.0}), (0.9999975002279671, {'toss': 130.0}), (0.999997950186933, {'toss': 132.0}), (0.9999983191532851, {'toss': 134.0}), (0.9999986217056938, {'toss': 136.0}), (0.9999988697986689, {'toss': 138.0}), (0.9999990732349086, {'toss': 140.0}), (0.9999992400526251, {'toss': 142.0}), (0.9999993768431523, {'toss': 144.0}), (0.9999993768431524, {'toss': 145.0}), (0.999999489011385, {'toss': 146.0}), (0.9999995809893357, {'toss': 148.0}), (0.9999996564112553, {'toss': 150.0}), (0.9999997182572293, {'toss': 152.0}), (0.999999768970928, {'toss': 154.0}), (0.9999998105561609, {'toss': 156.0}), (0.999999810556161, {'toss': 157.0}), (0.9999998446560521, {'toss': 158.0}), (0.9999998726179627, {'toss': 160.0}), (0.9999998955467295, {'toss': 162.0}), (0.9999999143483183, {'toss': 164.0}), (0.999999929765621, {'toss': 166.0}), (0.9999999424078091, {'toss': 168.0}), (0.9999999527744035, {'toss': 170.0}), (0.9999999612750108, {'toss': 172.0}), (0.9999999682455089, {'toss': 174.0}), (0.9999999739613172, {'toss': 176.0}), (0.9999999786482802, {'toss': 178.0}), (0.9999999824915897, {'toss': 180.0}), (0.9999999856431036, {'toss': 182.0}), (0.9999999882273449, {'toss': 184.0}), (0.9999999903464228, {'toss': 186.0}), (0.9999999920840668, {'toss': 188.0}), (0.9999999935089348, {'toss': 190.0}), (0.9999999946773265, {'toss': 192.0}), (0.9999999956354078, {'toss': 194.0}), (0.9999999964210343, {'toss': 196.0}), (0.9999999970652481, {'toss': 198.0}), (0.9999999975935034, {'toss': 200.0}), (0.9999999980266728, {'toss': 202.0}), (0.9999999983818717, {'toss': 204.0}), (0.9999999986731348, {'toss': 206.0}), (0.9999999989119706, {'toss': 208.0}), (0.9999999991078159, {'toss': 210.0}), (0.999999999268409, {'toss': 212.0}), (0.9999999994000953, {'toss': 214.0}), (0.9999999995080782, {'toss': 216.0}), (0.9999999995966241, {'toss': 218.0}), (0.9999999996692318, {'toss': 220.0}), (0.9999999997287701, {'toss': 222.0}), (0.9999999997775915, {'toss': 224.0}), (0.999999999817625, {'toss': 226.0}), (0.9999999998504525, {'toss': 228.0}), (0.9999999998773711, {'toss': 230.0}), (0.9999999998994443, {'toss': 232.0}), (0.9999999999175444, {'toss': 234.0}), (0.9999999999323864, {'toss': 236.0}), (0.9999999999445569, {'toss': 238.0}), (0.9999999999545365, {'toss': 240.0}), (0.9999999999627199, {'toss': 242.0}), (0.9999999999694303, {'toss': 244.0}), (0.9999999999749328, {'toss': 246.0}), (0.9999999999794449, {'toss': 248.0}), (0.999999999979445, {'toss': 249.0}), (0.9999999999831449, {'toss': 250.0}), (0.9999999999861788, {'toss': 252.0}), (0.9999999999886666, {'toss': 254.0}), (0.9999999999907067, {'toss': 256.0}), (0.9999999999923794, {'toss': 258.0}), (0.9999999999937511, {'toss': 260.0}), (0.9999999999948759, {'toss': 262.0}), (0.999999999994876, {'toss': 263.0}), (0.9999999999957984, {'toss': 264.0}), (0.9999999999965546, {'toss': 266.0}), (0.9999999999971748, {'toss': 268.0}), (0.9999999999976834, {'toss': 270.0}), (0.9999999999981004, {'toss': 272.0}), (0.9999999999984424, {'toss': 274.0}), (0.9999999999987382, {'toss': 276.0}), (0.9999999999989779, {'toss': 278.0}), (0.9999999999991722, {'toss': 280.0}), (0.9999999999993294, {'toss': 282.0})])
   4: 0.50000000 state: {} / returns: {"FairToss":"\"head\""}
   5: 0.50000000 state: {} / returns: {"FairToss":"\"tail\""}
```

{{% /expand %}}

## Cache and Latency
Let us introduce a slightly more complexity. Performance model a request handler,
that looks up a cache, if there is a cache hit, return immediately. Else, look up the database.

When the data is found in the db, it takes some time, but when the data is not present, the latency is lower.
(For example: index lookup or bloom filters lookup is usually faster and return not found, but
when it has to read the data, it would usually be slower)

What is the impact of the cache on the latency and how does it change with the cache hit ratio?

{{% hint %}}
In the code below, notice that we are not using any ids or values or dictionaries to implement
the cache etc. This is the crux of modeling, and why modeling is so simpler and faster than doing an
actual implementation and then measuring the performance

At a high level, the way you will describe this sequence of steps in a white board is literally,
1. Look up the cache
2. If found in cache, return
3. Else, look at the db

FizzBee you can describe and analyze the system at the same level of abstraction
as you think instead of bogged down by unnecessary implementation details.

{{% /hint %}}

`samples/cache/Cache.fizz`:
```python
atomic action Lookup:
  cached = LookupCache()
  if cached == "hit":
      return cached
  found = LookupDB()
  return found

func LookupCache():
  oneof:
    `hit` return "hit"
    `miss` return "miss"

func LookupDB():
  oneof:
    `found` return "found"
    `notfound` return "notfound"

```
As before, set the `maxActions: 1` in the `fizz.yaml` file.

Run the behavioral model checker `fizz samples/cache/Cache.fizz`. 
{{% graphviz %}}
digraph G {
"0x140001217a0" [label="init
Actions: 0, Forks: 0

", color="black" penwidth="2" ];
"0x140001217a0" -> "0x140001218c0" [label="Lookup[LookupCache.call]", color="black" penwidth="1" ];
"0x140001218c0" [label="Lookup
Actions: 1, Forks: 1

Threads: 0/1
", color="black" penwidth="1" ];
"0x140001218c0" -> "0x1400020c1e0" [label="[LookupCache.hit]", color="black" penwidth="1" ];
"0x1400020c1e0" [label="yield
Actions: 1, Forks: 2
Returns: {\"Lookup\":\"\"hit\"\"}
", color="black" penwidth="2" ];
"0x140001218c0" -> "0x1400020c3c0" [label="[LookupCache.miss, LookupDB.call]", color="black" penwidth="1" ];
"0x1400020c3c0" [label="Stmt:1
Actions: 1, Forks: 2

Threads: 0/1
", color="black" penwidth="1" ];
"0x1400020c3c0" -> "0x1400020d080" [label="[LookupDB.found]", color="black" penwidth="1" ];
"0x1400020d080" [label="yield
Actions: 1, Forks: 3
Returns: {\"Lookup\":\"\"found\"\"}
", color="black" penwidth="2" ];
"0x1400020c3c0" -> "0x1400020d260" [label="[LookupDB.notfound]", color="black" penwidth="1" ];
"0x1400020d260" [label="yield
Actions: 1, Forks: 3
Returns: {\"Lookup\":\"\"notfound\"\"}
", color="black" penwidth="2" ];
}

{{% /graphviz %}}

Now, define the performance model.

`samples/cache/perf_model.yaml`:
```yaml
configs:
  LookupCache.call:
    counters:
      latency_ms:
        numeric: 10
  LookupCache.hit:
    probability: 0.2
  LookupCache.miss:
    probability: 0.8

  LookupDB.found:
    probability: 0.9
    counters:
      latency_ms:
        numeric: 100
  LookupDB.notfound:
    probability: 0.1
    counters_ms:
      latency:
        numeric: 30

```
Run the performance model checker. You will see,
```bash
Metrics(mean={'latency_ms': 84.4}, histogram=[(0.2, {'latency_ms': 10.0}), (1.0000000000000002, {'latency_ms': 103.0})])
   2: 0.20000000 state: {} / returns: {"Lookup":"\"hit\""}
   4: 0.72000000 state: {} / returns: {"Lookup":"\"found\""}
   5: 0.08000000 state: {} / returns: {"Lookup":"\"notfound\""}
```
That is, with 20% cache hit ratio, the mean latency is 84.4.
20% of the time, data from the cache will be returned with 10ms latency.
72% of the time, data is found in the db, and 8% of the time, data is not found in the db.

Now, instead of 0.2, if you change the cache hit ratio to 0.8, you will see the mean latency is 28.6.
```python
Metrics(mean={'latency_ms': 28.6}, histogram=[(0.8, {'latency_ms': 10.0}), (1.0, {'latency_ms': 103.0})])
   2: 0.80000000 state: {} / returns: {"Lookup":"\"hit\""}
   4: 0.18000000 state: {} / returns: {"Lookup":"\"found\""}
   5: 0.02000000 state: {} / returns: {"Lookup":"\"notfound\""}
```

### Multiple counters
In the previous example, we saw only a single counter. We can have multiple counters defined the same way.

For example, let us say, you are using a cache service and hosted db service that charges
per API call, then you can get the estimated cost of the service.

`samples/cache/perf_model.yaml`:
```yaml
configs:
  LookupCache.call:
    counters:
      latency_ms:
        numeric: 10
    counters:
      cost:
        numeric: 0.00001
  LookupCache.hit:
    probability: 0.2
  LookupCache.miss:
    probability: 0.8

  LookupDB.call:
    counters:
      cost:
        numeric: 0.0001
        
  LookupDB.found:
    probability: 0.9
    counters:
      latency_ms:
        numeric: 100
      db_hits:
        numeric: 1
  LookupDB.notfound:
    probability: 0.1
    counters:
      latency_ms:
        numeric: 30



```

## Probability Distributions
In the examples so far, we saw the counters defined using simple `numeric` value.
It is good enough in some cases, but in many real applications like latencies,
using `mean` latency as a simple numeric value isn't good enough. 
We are usually interested in the tail. In that case, even for the dependencies,
we have to use the latencies.

Instead of using `numeric`, we can use the `distribution` to define the latency distribution.

Note: To give the maximum power and ease of use, FizzBee maintains the same semantics
as [scipy distributions](https://docs.scipy.org/doc/scipy/reference/stats.html#continuous-distributions). 
So, you can use any distribution that is available in scipy.

{{% hint %}}
If you only have some data points, you can create a histogram and use the `rv_histogram` distribution.
https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.rv_histogram.html#scipy.stats.rv_histogram
{{% /hint %}}

{{% hint type="caution" %}}
This is a work in progress, contact us if you face any issues.
{{% /hint %}}
```yaml
configs:
  LookupCache.call:
    counters:
      latency_ms:
        distribution: lognorm(s=0.3, loc=2)
  LookupCache.hit:
    probability: 0.2
  LookupCache.miss:
    probability: 0.8

  LookupDB.found:
    probability: 0.9
    counters:
      latency_ms:
        distribution: gamma(a=3, loc=100, scale=1)
  LookupDB.notfound:
    probability: 0.1
    counters_ms:
      latency:
        distribution: lognorm(s=0.5, loc=3)

```

If you use common cloud components, you can simply specify the latency profile.


```yaml
configs:
  LookupCache.call:
    counters:
      latency_ms:
        distribution: aws.elasticache.redis.read()
  LookupCache.hit:
    probability: 0.2
  LookupCache.miss:
    probability: 0.8

  LookupDB.found:
    probability: 0.9
    counters:
      latency_ms:
        distribution: aws.dynamodb.query()
  LookupDB.notfound:
    probability: 0.1
    counters_ms:
      latency:
        distribution: aws.dynamodb.query()

```

## More examples:
### Simulating Two dice with a fair coin
Now that we saw how to simulate a single die with a fair coin, let us see how to simulate two dice with a fair coin.
Here, unlike before, the required probabilities are not uniform. 

**samples/two-dice/Die.fizz**
```python
atomic func Toss():
    oneof:
        return 0
        return 1

atomic func RollDie():
  toss0 = Toss()
  while True:
    toss1 = Toss()
    toss2 = Toss()

    if (toss0 != toss1 or toss0 != toss2):
      return 4 * toss0 + 2 * toss1 + toss2

atomic action TwoDice:
  die1 = RollDie()
  die2 = RollDie()
  return die1 + die2
  
```

**samples/two-dice/perf_model.yaml**
```yaml
configs:
  Toss.call:
    counters:
      toss:
        numeric: 1

```

**samples/two-dice/fizz.yaml**
```yaml
options:
  maxActions: 1
```

Run both the behavioral and performance model checkers.
```bash
Metrics(mean={'toss': 7.333333333332462}, histogram=[(0.5625, {'toss': 6.4375}), (0.84375, {'toss': 7.794642857142858}), (0.94921875, {'toss': 9.119642857142859}), (0.984375, {'toss': 10.427335164835167}), (0.995361328125, {'toss': 11.724210164835167}), (0.9986572265625, {'toss': 13.013683849045693}), (0.9996185302734375, {'toss': 14.297774758136601}), (0.9998931884765625, {'toss': 15.5777747581366}), (0.9999704360961914, {'toss': 16.854560472422314}), (0.9999918937683105, {'toss': 18.12875402080941}), (0.9999977946281433, {'toss': 19.400812844338823}), (0.9999994039535522, {'toss': 20.671083114609093}), (0.9999998398125172, {'toss': 21.939833114609094}), (0.9999999571591616, {'toss': 23.20727497507421}), (0.9999999885912985, {'toss': 24.473579322900296}), (0.9999999969732016, {'toss': 25.738885445349275}), (0.9999999991996447, {'toss': 27.003308522272352}), (0.9999999997889972, {'toss': 28.266944885908718}), (0.9999999999445208, {'toss': 29.529875920391476}), (0.9999999999854481, {'toss': 30.79217100235869}), (0.9999999999961915, {'toss': 32.053889752358685}), (0.9999999999962482, {'toss': 33.053889752358685}), (0.999999999999062, {'toss': 33.315083782209435}), (0.9999999999990623, {'toss': 34.315083782209435})])
  50: 0.02777778 state: {} / returns: {"TwoDice":"2"}
  51: 0.05555556 state: {} / returns: {"TwoDice":"3"}
  52: 0.08333333 state: {} / returns: {"TwoDice":"4"}
  53: 0.11111111 state: {} / returns: {"TwoDice":"5"}
  54: 0.13888889 state: {} / returns: {"TwoDice":"6"}
  55: 0.16666667 state: {} / returns: {"TwoDice":"7"}
  56: 0.13888889 state: {} / returns: {"TwoDice":"8"}
  57: 0.11111111 state: {} / returns: {"TwoDice":"9"}
  58: 0.08333333 state: {} / returns: {"TwoDice":"10"}
  59: 0.05555556 state: {} / returns: {"TwoDice":"11"}
  60: 0.02777778 state: {} / returns: {"TwoDice":"12"}
```


### Even more complex examples
We will see more examples on how these can be used for performance modeling actual distributed systems in the next article.

## Conclusion
In this tutorial, we saw how to model the performance of a system using FizzBee's python'ish language.
At present, the features are limited, but we will add much better query languages.