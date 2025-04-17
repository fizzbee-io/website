---
title: Time oblivious Sampling Algorithm for Random Variate Generation
weight: 30
aliases:
  - "/examples/time-oblivious-sampling-algorithm/"
---

Given a fair random bit generator, how do you generate random numbers with arbitrary probabilities?

Previously we saw the [Knuth-Yao algorithm](/examples/knuth-yao-sampling-algorithm/)
for generating random variates with arbitrary probabilities. We showed how to model the algorithm in FizzBee and
looked at the number of random bits used on average and showed that the
number of bits used (or time to output) depends on the output generated.

In this post, we will see and analyze a time-oblivious sampling algorithm for random variate generation
based on the paper [Resistance to Timing Attacks for Sampling and
Privacy Preserving Schemes](https://drops.dagstuhl.de/storage/00lipics/lipics-vol256-forc2023/LIPIcs.FORC.2023.11/LIPIcs.FORC.2023.11.pdf).

## The Algorithm

{{< rawhtml >}}
<a href="https://ibb.co/C7ft1NV"><img src="https://i.ibb.co/4THfm94/time-oblivious-sampling-algorithm.png" alt="time-oblivious-sampling-algorithm" border="0"></a>
{{</rawhtml>}}

For an algorithm, consider the following probabilities `[1/2, 1/3, 1/6]`.

{{< rawhtml >}}
<a href="https://imgbb.com/"><img src="https://i.ibb.co/qC1XwjN/Screenshot-2024-06-02-at-5-08-05-PM.png" alt="Screenshot-2024-06-02-at-5-08-05-PM" border="0"></a><br /><a target='_blank' href='https://imgbb.com/'>free picture hosting for ebay</a><br />
{{</rawhtml>}}

### Simplifying the algorithm
For this, I am simplifying the code to some extent. In the original code,
there are references to LCM of the denominators of the probabilities. But for the sake of simplicity,
I am assuming the input is given with such that the denominator is already the LCM.
That is, `[1/2, 1/3, 1/6]` is given as `[3/6, 2/6, 1/6]`.
The, the array P is `[3, 2, 1]` and Q = 6.

There is another reference to binary search, that is actually not required, as
you could do an early return from within the for loop.

And finally, you can see in the graph that after input 11, it is the same as reaching
the root. So, we will simplify the graph such that after 11, the graph will go to
the root. This will reduce the solution to bounded state space.

## FizzBee Spec

{{% fizzbee %}}
# Time oblivious algorithm for Random Variate Generation
# FizzBee representation of https://drops.dagstuhl.de/storage/00lipics/lipics-vol256-forc2023/LIPIcs.FORC.2023.11/LIPIcs.FORC.2023.11.pdf

P = [3, 2, 1]
Q = 6

REQUIRED_LEVEL = math.ceil(math.log(Q, 2))

action Init:
  value = -1
  random_bits = ''

atomic func RandomBit():
  oneof:
    `zero` return 0
    `one` return 1

atomic action GenRandomValue:
    if value != -1:
        return value

    random_bits = ''
    while True:
        bit = RandomBit()
        random_bits = random_bits + str(bit)
        leaf_nodes = 1 << len(random_bits)
        random_int = int(random_bits, 2)
        if random_int >= Q/2 and len(random_bits) == REQUIRED_LEVEL-1:
            random_bits = ''
            continue

        if leaf_nodes  >= Q:
            value = GetValue(random_int)
            #random_bits = ''
            return value


atomic func GetValue(j):
    cumulative = 0
    for i in range(0, len(P)):
        cumulative = cumulative + P[i]
        if j < cumulative:
            return i

{{% /fizzbee %}}

You can run this in the FizzBee playground and see the state graph.
This graph is actually the mirror image of the DDG tree shown above. 
The algorithm takes the left link on 1 and right link on 0.

{{% graphviz %}}
digraph G {
  "0x14000121c80" [label="yield
Actions: 0, Forks: 0
State: {\"random_bits\":\"\"\"\",\"value\":\"-1\"}
", color="black" penwidth="2" ];
  "0x14000121c80" -> "0x140002161e0" [label="GenRandomValue[RandomBit.call]", color="black" penwidth="1" ];
  "0x140002161e0" [label="GenRandomValue
Actions: 1, Forks: 1
State: {\"random_bits\":\"\"\"\",\"value\":\"-1\"}
Threads: 0/1
", color="black" penwidth="1" ];
  "0x140002161e0" -> "0x14000216fc0" [label="[RandomBit.zero, RandomBit.call]", color="black" penwidth="1" ];
  "0x14000216fc0" [label="Stmt:0
Actions: 1, Forks: 2
State: {\"random_bits\":\"\"0\"\",\"value\":\"-1\"}
Threads: 0/1
", color="black" penwidth="1" ];
  "0x14000216fc0" -> "0x1400025cae0" [label="[RandomBit.zero, RandomBit.call]", color="black" penwidth="1" ];
  "0x1400025cae0" [label="Stmt:0
Actions: 1, Forks: 3
State: {\"random_bits\":\"\"00\"\",\"value\":\"-1\"}
Threads: 0/1
", color="black" penwidth="1" ];
  "0x1400025cae0" -> "0x140002abce0" [label="[RandomBit.zero, GetValue.call]", color="black" penwidth="1" ];
  "0x140002abce0" [label="yield
Actions: 1, Forks: 4
State: {\"random_bits\":\"\"000\"\",\"value\":\"0\"}Returns: {\"GenRandomValue\":\"0\"}
", color="black" penwidth="2" ];
  "0x140002abce0" -> "0x140002abce0" [label="GenRandomValue", color="black" penwidth="1" ];
  "0x1400025cae0" -> "0x140002fe000" [label="[RandomBit.one, GetValue.call]", color="black" penwidth="1" ];
  "0x140002fe000" [label="yield
Actions: 1, Forks: 4
State: {\"random_bits\":\"\"001\"\",\"value\":\"0\"}Returns: {\"GenRandomValue\":\"0\"}
", color="black" penwidth="2" ];
  "0x140002fe000" -> "0x140002fe000" [label="GenRandomValue", color="black" penwidth="1" ];
  "0x14000216fc0" -> "0x1400025cd80" [label="[RandomBit.one, RandomBit.call]", color="black" penwidth="1" ];
  "0x1400025cd80" [label="Stmt:1
Actions: 1, Forks: 3
State: {\"random_bits\":\"\"01\"\",\"value\":\"-1\"}
Threads: 0/1
", color="black" penwidth="1" ];
  "0x1400025cd80" -> "0x1400002a5a0" [label="[RandomBit.zero, GetValue.call]", color="black" penwidth="1" ];
  "0x1400002a5a0" [label="yield
Actions: 1, Forks: 4
State: {\"random_bits\":\"\"010\"\",\"value\":\"0\"}Returns: {\"GenRandomValue\":\"0\"}
", color="black" penwidth="2" ];
  "0x1400002a5a0" -> "0x1400002a5a0" [label="GenRandomValue", color="black" penwidth="1" ];
  "0x1400025cd80" -> "0x1400002a840" [label="[RandomBit.one, GetValue.call]", color="black" penwidth="1" ];
  "0x1400002a840" [label="yield
Actions: 1, Forks: 4
State: {\"random_bits\":\"\"011\"\",\"value\":\"1\"}Returns: {\"GenRandomValue\":\"1\"}
", color="black" penwidth="2" ];
  "0x1400002a840" -> "0x1400002a840" [label="GenRandomValue", color="black" penwidth="1" ];
  "0x140002161e0" -> "0x14000217260" [label="[RandomBit.one, RandomBit.call]", color="black" penwidth="1" ];
  "0x14000217260" [label="Stmt:1
Actions: 1, Forks: 2
State: {\"random_bits\":\"\"1\"\",\"value\":\"-1\"}
Threads: 0/1
", color="black" penwidth="1" ];
  "0x14000217260" -> "0x140002aa420" [label="[RandomBit.zero, RandomBit.call]", color="black" penwidth="1" ];
  "0x140002aa420" [label="Stmt:0
Actions: 1, Forks: 3
State: {\"random_bits\":\"\"10\"\",\"value\":\"-1\"}
Threads: 0/1
", color="black" penwidth="1" ];
  "0x140002aa420" -> "0x1400002be60" [label="[RandomBit.zero, GetValue.call]", color="black" penwidth="1" ];
  "0x1400002be60" [label="yield
Actions: 1, Forks: 4
State: {\"random_bits\":\"\"100\"\",\"value\":\"1\"}Returns: {\"GenRandomValue\":\"1\"}
", color="black" penwidth="2" ];
  "0x1400002be60" -> "0x1400002be60" [label="GenRandomValue", color="black" penwidth="1" ];
  "0x140002aa420" -> "0x140003cc180" [label="[RandomBit.one, GetValue.call]", color="black" penwidth="1" ];
  "0x140003cc180" [label="yield
Actions: 1, Forks: 4
State: {\"random_bits\":\"\"101\"\",\"value\":\"2\"}Returns: {\"GenRandomValue\":\"2\"}
", color="black" penwidth="2" ];
  "0x140003cc180" -> "0x140003cc180" [label="GenRandomValue", color="black" penwidth="1" ];
  "0x14000217260" -> "0x140002161e0" [label="[RandomBit.one, RandomBit.call]", color="black" penwidth="1" ];
}
{{< /graphviz >}}


## Probabilistic Model Checking
Now, let us evaluate the actual probabilities of the generated numbers. The 
probabilistic evaluation is not supported in the online playground yet, until then
you can install [FizzBee locally following the instructions](https://github.com/fizzbee-io/fizzbee?tab=readme-ov-file#run-a-model-checker).

```bash
./fizz samples/timeoblivious-sampling/TimeObliviousSampling.fizz
Model checking samples/timeoblivious-sampling/TimeObliviousSampling.json
configFileName: samples/timeoblivious-sampling/fizz.yaml
StateSpaceOptions: options:{max_actions:100  max_concurrent_actions:5}  action_options:{key:"GenRandomValue"  value:{max_actions:1}}
Nodes: 13, elapsed: 3.508375ms
Time taken for model checking: 3.522458ms
Writen graph dotfile: samples/timeoblivious-sampling/out/run_2024-06-02_17-42-33/graph.dot
To generate svg, run: 
dot -Tsvg samples/timeoblivious-sampling/out/run_2024-06-02_17-42-33/graph.dot -o graph.svg && open graph.svg
Max Depth 4
PASSED: Model checker completed successfully
Writen 1 node files and 1 link files to dir samples/timeoblivious-sampling/out/run_2024-06-02_17-42-33
```
For smaller state spaces, this will generate the graph as in the playground.
Also, take note of the paths, the json file path and the output directory path, as you will need them to generate the graph.

### Set the probabilities and cost
In this example, there is only one place where the non-determinism happens. It is at 
choosing the random bits. By default FizzBee assumes, uniform distribution for the random bits.
But we can customize when required. 
Similarly, we can also assign the cost for each step.

To refer to the step for assigning probabilities and cost, we can use the labels. The labels are 
defined by prefixing with with backtick enclosed string. For example, we have
`zero` and `one` as labels for the random bits. To reference them, it will be
namespaced to the function or action name. So, to refer to the `zero` label in the `RandomBit` function,
it will be `RandomBit.zero`.

Now, create a file perf_model.yaml with the following content.
```yaml
configs:
  RandomBit.zero:
    counters:
      toss:
        numeric: 1
  RandomBit.one:
    counters:
      toss:
        numeric: 1
```
Here, any time the `zero` label is taken, the `toss` counter is incremented by 1.
Similarly, for the `one` label. In FizzBee cost/reward are referred to as counter.

For analyzing random number generation algorithms, it is customary to use
the number of coin tosses or the random bits used as the cost.

### Run the model checker

```bash
Metrics(mean={'toss': 3.666666567325592}, histogram=[(0.75, {'toss': 3.0}), (0.9375, {'toss': 5.0}), (0.984375, {'toss': 7.0}), (0.99609375, {'toss': 9.0}), (0.9990234375, {'toss': 11.0}), (0.999755859375, {'toss': 13.0}), (0.99993896484375, {'toss': 15.0}), (0.9999847412109375, {'toss': 17.0}), (0.9999961853027344, {'toss': 19.0}), (0.9999990463256836, {'toss': 21.0}), (0.9999997615814209, {'toss': 23.0}), (0.9999999403953552, {'toss': 25.0})])
     7: 0.166667 state: {'random_bits': '"000"', 'value': '0'} / returns: {}
     8: 0.166667 state: {'random_bits': '"001"', 'value': '0'} / returns: {}
     9: 0.166667 state: {'random_bits': '"010"', 'value': '0'} / returns: {}
    10: 0.166667 state: {'random_bits': '"011"', 'value': '1'} / returns: {}
    11: 0.166667 state: {'random_bits': '"100"', 'value': '1'} / returns: {}
    12: 0.166667 state: {'random_bits': '"101"', 'value': '2'} / returns: {}
```

You can actually see the generated probabilities and the mean and the histogram
for the time to complete. 

If you sum up the probabilities for each return value, you will see the probabilities match.

You will also see the cost of average number of tosses to reach each of these states.

```bash
Cost to reach terminal states:
     7: {'toss': 3.666666567325592}
     8: {'toss': 3.666666567325592}
     9: {'toss': 3.666666567325592}
    10: {'toss': 3.666666567325592}
    11: {'toss': 3.666666567325592}
    12: {'toss': 3.666666567325592}
```
That is, on average, it takes 3.67 tosses to generate the output
and the output is independent of the time taken to generate the output.

This fixes the side channel vulnerability in the Knuth-Yao algorithm.


### Reducing the possible output space
In the above implementation, we made the generated graph to match the DDG tree. But in practice, 
we can reduce the number of output states, by keeping only one output state per output value.

Just remove the col=0 from the Init action. This will make the col variable to be a local variable.

{{% highlight udiff %}}
action Init:
  value = -1
-  random_bits='''
{{% /highlight %}}

Run the model checker again, and you will see the number of nodes reduced.

Now, run the performance model checker. You will see the output probabilities
for each return value summed as you would want.

```bash
Metrics(mean={'toss': 3.666666567325592}, histogram=[(0.75, {'toss': 3.0}), (0.9375, {'toss': 5.0}), (0.984375, {'toss': 7.0}), (0.99609375, {'toss': 9.0}), (0.9990234375, {'toss': 11.0}), (0.999755859375, {'toss': 13.0}), (0.99993896484375, {'toss': 15.0}), (0.9999847412109375, {'toss': 17.0}), (0.9999961853027344, {'toss': 19.0}), (0.9999990463256836, {'toss': 21.0}), (0.9999997615814209, {'toss': 23.0}), (0.9999999403953552, {'toss': 25.0})])
     7: 0.500000 state: {'value': '0'} / returns: {}
     8: 0.333333 state: {'value': '1'} / returns: {}
     9: 0.166667 state: {'value': '2'} / returns: {}
```

## Two Dice Problem
We previously solved the [two dice problem](/design/tutorials/performance-modeling/#simulating-two-dice-with-a-fair-coin) 
using a simpler approach that is non-optimal. It took a mean of `7.333333` tosses to generate the output.

Now, let us model the same problem using the Knuth-Yao algorithm.

For this, you just need to update the probabilities.
The probabilities for the two dice problem are `[1/36, 2/36, 3/36, 4/36, 5/36, 6/36, 5/36, 4/36, 3/36, 2/36, 1/36]`.

For this, just change the values for P and Q.
```python
Q=36
P=[1, 2, 3, 4, 5, 6, 5, 4, 3, 2, 1]
```

Now, run the model checker. 

```bash
./fizz samples/timeoblivious-sampling/TimeObliviousSampling.fizz
Model checking samples/timeoblivious-sampling/TimeObliviousSampling.json
configFileName: samples/timeoblivious-sampling/fizz.yaml
StateSpaceOptions: options:{max_actions:100  max_concurrent_actions:5}  action_options:{key:"GenRandomValue"  value:{max_actions:1}}
Nodes: 61, elapsed: 26.9405ms
Time taken for model checking: 26.959208ms
Writen graph dotfile: samples/timeoblivious-sampling/out/run_2024-06-02_17-52-51/graph.dot
To generate svg, run: 
dot -Tsvg samples/timeoblivious-sampling/out/run_2024-06-02_17-52-51/graph.dot -o graph.svg && open graph.svg
Max Depth 7
PASSED: Model checker completed successfully
Writen 1 node files and 1 link files to dir samples/timeoblivious-sampling/out/run_2024-06-02_17-52-51
```

Now, run the performance model checker.

```bash
Metrics(mean={'toss': 9.888887849609615}, histogram=[(0.5625, {'toss': 6.0}), (0.80859375, {'toss': 11.0}), (0.916259765625, {'toss': 16.0}), (0.9633636474609375, {'toss': 21.0}), (0.9839715957641602, {'toss': 26.0}), (0.9929875731468201, {'toss': 31.0}), (0.9969320632517338, {'toss': 36.0}), (0.9986577776726335, {'toss': 41.0}), (0.9994127777317772, {'toss': 46.0}), (0.9997430902576525, {'toss': 51.0}), (0.999887601987723, {'toss': 56.0}), (0.9999508258696288, {'toss': 61.0}), (0.9999784863179626, {'toss': 66.0}), (0.9999784863179628, {'toss': 67.0}), (0.9999784863179628, {'toss': 69.0}), (0.9999905877641088, {'toss': 71.0}), (0.9999905877641087, {'toss': 74.0}), (0.9999958821467975, {'toss': 76.0}), (0.9999958821467978, {'toss': 77.0}), (0.9999981984392241, {'toss': 81.0}), (0.9999992118171604, {'toss': 86.0}), (0.9999992118171606, {'toss': 87.0}), (0.9999992118171606, {'toss': 89.0}), (0.9999996551700079, {'toss': 91.0}), (0.9999996551700079, {'toss': 93.0}), (0.9999996551700079, {'toss': 95.0}), (0.9999998491368783, {'toss': 96.0})])
    50: 0.027778 state: {'value': '0'} / returns: {}
    51: 0.055556 state: {'value': '1'} / returns: {}
    52: 0.083333 state: {'value': '2'} / returns: {}
    53: 0.111111 state: {'value': '3'} / returns: {}
    54: 0.138889 state: {'value': '4'} / returns: {}
    55: 0.166667 state: {'value': '5'} / returns: {}
    56: 0.138889 state: {'value': '6'} / returns: {}
    57: 0.111111 state: {'value': '7'} / returns: {}
    58: 0.083333 state: {'value': '8'} / returns: {}
    59: 0.055556 state: {'value': '9'} / returns: {}
    60: 0.027778 state: {'value': '10'} / returns: {}
```

As you can see, this algorith takes on average `9.89` tosses to generate the output,
where as the Knuth-Yao algorithm takes `3.67` tosses. But, this algorithm
is secure from side channels attacks.

## Conclusion
In this post, we saw the time oblivious sampling algorithm for random variate generation.
And, how to analyze algorithms for probability and performance characteristics
typically necessary for cryptographic algorithms.

Learn more about how to use FizzBee by going through the [tutorials](/design/tutorials/).



