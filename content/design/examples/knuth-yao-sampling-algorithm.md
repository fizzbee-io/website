---
title: Knuth-Yao Sampling Algorithm for Random Variate Generation
weight: 30
---

Given a fair coin, how do you generate random numbers with arbitrary probabilities?

There were a few simple algorithms in the [performance analysis](/design/tutorials/performance-modeling/) tutorial.
But what if you have a more complex distribution?

The Knuth-Yao algorithm is a general method to generate random variates with arbitrary probabilities, it is also
proven to be the optimal method in terms of expected number of coin flips.

## The Algorithm

Let us say, you have to generate 3 numbers with probabilities, `[0.4375, 0.40625, 0.15625]`,
then, first express this decimal number in binary: `[0.01110, 0.01101, 0.00101]`.

The algorithm is better explained with details at:
[https://www.esat.kuleuven.be/cosic/blog/constant-time-discrete-gaussian-sampling-for-lattice-based-cryptography/](https://www.esat.kuleuven.be/cosic/blog/constant-time-discrete-gaussian-sampling-for-lattice-based-cryptography/)

The algorithm works by constructing a binary tree called _discrete distribution generating (DDG)_ tree
as shown in this image.
    
{{< figure src="https://www.esat.kuleuven.be/cosic/wp-content/uploads/2018/03/img2.png" alt="Knuth-Yao Algorithm DDG Tree" >}}
(source: [KU Leuven](https://www.esat.kuleuven.be/cosic/blog/constant-time-discrete-gaussian-sampling-for-lattice-based-cryptography/))

The [full pseudocode and detailed explanation](https://www.esat.kuleuven.be/cosic/blog/constant-time-discrete-gaussian-sampling-for-lattice-based-cryptography/).

### Repeating rationals
Although the algorithm shows only for fixed point, or non repeating rationals, it can technically be 
used for repeating rationals like generating with a probabilities `[1/2, 1/3, 1/6]` as well with a tiny change. The change will be shown
in the FizzBee spec.
For example: 1/6 = 0.0010101..., then in code, we simply put,
0.001 and say repeat last 2 digits.
And, to simplify the implementation, when we have different probabilities with different number of
non-repeating digits and repeating, we'll make the number of columns fixed, and adjust the repeat variable to match
all the probabilities.
1/6 = 0.0010101... = 0.0(01) = 0.00(10) = 0.00101(010101)


## FizzBee Spec

{{% fizzbee %}}
# Knuth-Yao Sampling Algorithm for Random Variate Generation
# FizzBee representation of https://www.esat.kuleuven.be/cosic/blog/constant-time-discrete-gaussian-sampling-for-lattice-based-cryptography/

P = [('01110'), ('01101'), ('00101')]   # (1/4+1/8+1/16), (1/4+1/8+1/32), (1/8+1/32)
MAX_COLS = 5
# Only relevant for repeating rationals.
REPEATS = 0

action Init:
  value = -1
  col=0

atomic func RandomBit():
  oneof:
    `zero` return 0
    `one` return 1

atomic fair action Roll:
    if value > -1:
        # We are modeling a single call, so if already computed, ignore
        return value

    d, col = 0, 0

    while True:
        r = RandomBit()
        d = 2*d + r

        for row in range(len(P) - 1, -1, -1):
            d = d - int(P[row][col])
            if d == -1:
                value = row
                return value
        col = col + 1
        if col >= MAX_COLS:
            col -= REPEATS

    return value

{{% /fizzbee %}}

You can run this in the FizzBee playground and see the state graph.
This graph is actually the mirror image of the DDG tree shown above. 
The algorithm takes the left link on 1 and right link on 0.

{{% graphviz %}}
digraph G {
  "0x1400012fb00" [label="yield
Actions: 0, Forks: 0
State: {\"col\":\"0\",\"value\":\"-1\"}
", color="black" penwidth="2" ];
  "0x1400012fb00" -> "0x1400021e000" [label="Roll[RandomBit.call]", color="black" penwidth="1" ];
  "0x1400021e000" [label="Roll
Actions: 1, Forks: 1
State: {\"col\":\"0\",\"value\":\"-1\"}
Threads: 0/1
", color="black" penwidth="1" ];
  "0x1400021e000" -> "0x1400021ede0" [label="[RandomBit.zero, RandomBit.call]", color="black" penwidth="1" ];
  "0x1400021ede0" [label="Stmt:0
Actions: 1, Forks: 2
State: {\"col\":\"1\",\"value\":\"-1\"}
Threads: 0/1
", color="black" penwidth="1" ];
  "0x1400021ede0" -> "0x14000268b40" [label="[RandomBit.zero]", color="black" penwidth="1" ];
  "0x14000268b40" [label="yield
Actions: 1, Forks: 3
State: {\"col\":\"1\",\"value\":\"1\"}Returns: {\"Roll\":\"1\"}
", color="black" penwidth="2" ];
  "0x14000268b40" -> "0x14000268b40" [label="Roll", color="black" penwidth="1" ];
  "0x1400021ede0" -> "0x14000268de0" [label="[RandomBit.one]", color="black" penwidth="1" ];
  "0x14000268de0" [label="yield
Actions: 1, Forks: 3
State: {\"col\":\"1\",\"value\":\"0\"}Returns: {\"Roll\":\"0\"}
", color="black" penwidth="2" ];
  "0x14000268de0" -> "0x14000268de0" [label="Roll", color="black" penwidth="1" ];
  "0x1400021e000" -> "0x1400021f080" [label="[RandomBit.one, RandomBit.call]", color="black" penwidth="1" ];
  "0x1400021f080" [label="Stmt:1
Actions: 1, Forks: 2
State: {\"col\":\"1\",\"value\":\"-1\"}
Threads: 0/1
", color="black" penwidth="1" ];
  "0x1400021f080" -> "0x140002b4720" [label="[RandomBit.zero, RandomBit.call]", color="black" penwidth="1" ];
  "0x140002b4720" [label="Stmt:0
Actions: 1, Forks: 3
State: {\"col\":\"2\",\"value\":\"-1\"}
Threads: 0/1
", color="black" penwidth="1" ];
  "0x140002b4720" -> "0x14000307260" [label="[RandomBit.zero]", color="black" penwidth="1" ];
  "0x14000307260" [label="yield
Actions: 1, Forks: 4
State: {\"col\":\"2\",\"value\":\"2\"}Returns: {\"Roll\":\"2\"}
", color="black" penwidth="2" ];
  "0x14000307260" -> "0x14000307260" [label="Roll", color="black" penwidth="1" ];
  "0x140002b4720" -> "0x14000307500" [label="[RandomBit.one]", color="black" penwidth="1" ];
  "0x14000307500" [label="yield
Actions: 1, Forks: 4
State: {\"col\":\"2\",\"value\":\"1\"}Returns: {\"Roll\":\"1\"}
", color="black" penwidth="2" ];
  "0x14000307500" -> "0x14000307500" [label="Roll", color="black" penwidth="1" ];
  "0x1400021f080" -> "0x140002b49c0" [label="[RandomBit.one, RandomBit.call]", color="black" penwidth="1" ];
  "0x140002b49c0" [label="Stmt:1
Actions: 1, Forks: 3
State: {\"col\":\"2\",\"value\":\"-1\"}
Threads: 0/1
", color="black" penwidth="1" ];
  "0x140002b49c0" -> "0x14000354e40" [label="[RandomBit.zero]", color="black" penwidth="1" ];
  "0x14000354e40" [label="yield
Actions: 1, Forks: 4
State: {\"col\":\"2\",\"value\":\"0\"}Returns: {\"Roll\":\"0\"}
", color="black" penwidth="2" ];
  "0x14000354e40" -> "0x14000354e40" [label="Roll", color="black" penwidth="1" ];
  "0x140002b49c0" -> "0x140003550e0" [label="[RandomBit.one, RandomBit.call]", color="black" penwidth="1" ];
  "0x140003550e0" [label="Stmt:1
Actions: 1, Forks: 4
State: {\"col\":\"3\",\"value\":\"-1\"}
Threads: 0/1
", color="black" penwidth="1" ];
  "0x140003550e0" -> "0x140003e6360" [label="[RandomBit.zero]", color="black" penwidth="1" ];
  "0x140003e6360" [label="yield
Actions: 1, Forks: 5
State: {\"col\":\"3\",\"value\":\"0\"}Returns: {\"Roll\":\"0\"}
", color="black" penwidth="2" ];
  "0x140003e6360" -> "0x140003e6360" [label="Roll", color="black" penwidth="1" ];
  "0x140003550e0" -> "0x140003e6600" [label="[RandomBit.one, RandomBit.call]", color="black" penwidth="1" ];
  "0x140003e6600" [label="Stmt:1
Actions: 1, Forks: 5
State: {\"col\":\"4\",\"value\":\"-1\"}
Threads: 0/1
", color="black" penwidth="1" ];
  "0x140003e6600" -> "0x14000430c00" [label="[RandomBit.zero]", color="black" penwidth="1" ];
  "0x14000430c00" [label="yield
Actions: 1, Forks: 6
State: {\"col\":\"4\",\"value\":\"2\"}Returns: {\"Roll\":\"2\"}
", color="black" penwidth="2" ];
  "0x14000430c00" -> "0x14000430c00" [label="Roll", color="black" penwidth="1" ];
  "0x140003e6600" -> "0x14000430ea0" [label="[RandomBit.one]", color="black" penwidth="1" ];
  "0x14000430ea0" [label="yield
Actions: 1, Forks: 6
State: {\"col\":\"4\",\"value\":\"1\"}Returns: {\"Roll\":\"1\"}
", color="black" penwidth="2" ];
  "0x14000430ea0" -> "0x14000430ea0" [label="Roll", color="black" penwidth="1" ];
}
{{< /graphviz >}}


## Probabilistic Model Checking
Now, let us evaluate the actual probabilities of the generated numbers. The 
probabilistic evaluation is not supported in the online playground yet, until then
you can install [FizzBee locally following the instructions](https://github.com/fizzbee-io/fizzbee?tab=readme-ov-file#run-a-model-checker).

```bash
./fizz samples/knuthyaosampling/KnuthYaoSampling.fizz                                                  
Model checking samples/knuthyaosampling/KnuthYaoSampling.json
configFileName: samples/knuthyaosampling/fizz.yaml
fizz.yaml not found. Using default options
StateSpaceOptions: options:{max_actions:100  max_concurrent_actions:2}
Nodes: 16, elapsed: 4.202042ms
Time taken for model checking: 4.216ms
Writen graph dotfile: samples/knuthyaosampling/out/run_2024-06-02_15-13-11/graph.dot
To generate svg, run: 
dot -Tsvg samples/knuthyaosampling/out/run_2024-06-02_15-13-11/graph.dot -o graph.svg && open graph.svg
Max Depth 6
PASSED: Model checker completed successfully
Writen 1 node files and 1 link files to dir samples/knuthyaosampling/out/run_2024-06-02_15-13-11
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
bazel-bin/performance/performance_bin \
    --state samples/knuthyaosampling/out/run_2024-06-02_15-22-05/ \
    --source samples/knuthyaosampling/KnuthYaoSampling.json  --perf samples/knuthyaosampling/perf_model.yaml

Metrics(mean={'toss': 2.6875}, histogram=[(0.5, {'toss': 2.0}), (0.875, {'toss': 3.0}), (0.9375, {'toss': 4.0}), (1.0, {'toss': 5.0})])
     4: 0.250000 state: {'col': '1', 'value': '1'} / returns: {"Roll":"1"}
     5: 0.250000 state: {'col': '1', 'value': '0'} / returns: {"Roll":"0"}
     8: 0.125000 state: {'col': '2', 'value': '2'} / returns: {"Roll":"2"}
     9: 0.125000 state: {'col': '2', 'value': '1'} / returns: {"Roll":"1"}
    10: 0.125000 state: {'col': '2', 'value': '0'} / returns: {"Roll":"0"}
    12: 0.062500 state: {'col': '3', 'value': '0'} / returns: {"Roll":"0"}
    14: 0.031250 state: {'col': '4', 'value': '2'} / returns: {"Roll":"2"}
    15: 0.031250 state: {'col': '4', 'value': '1'} / returns: {"Roll":"1"}
```

You can actually see the generated probabilities and the mean and the histogram
for the time to complete. That is 50% of the time, it takes 2 coin tosses, 37.5% of the time it takes 3 coin tosses, etc.

If you sum up the probabilities for each return value, you will see the probabilities match.

You will also see the cost of average number of tosses to reach each of these states.

```bash
Cost to reach terminal states:
     4: {'toss': 2.0}
     5: {'toss': 2.0}
     8: {'toss': 3.0}
     9: {'toss': 3.0}
    10: {'toss': 3.0}
    12: {'toss': 4.0}
    14: {'toss': 5.0}
    15: {'toss': 5.0}

```

### Security vulnerability
If you noticed, the time taken to generate the output depends on the output generated.
This opens this algorithm for a side-channel attack. The attacker can measure the time taken to generate the output
and make informed guess to narrow down the possible random numbers generated.

To mitigate this, we will later look at other [time-oblivious random variate generation](/examples/time-oblivious-sampling-algorithm/) algorithms 
in a later post.

### Reducing the possible output space
In the above implementation, we made the generated graph to match the DDG tree. But in practice, 
we can reduce the number of output states, by keeping only one output state per output value.

Just remove the col=0 from the Init action. This will make the col variable to be a local variable.

{{% highlight udiff %}}
action Init:
  value = -1
-  col=0
{{% /highlight %}}

Run the model checker again, and you will see the number of nodes reduced.

Now, run the performance model checker. You will see the output probabilities
for each return value summed as you would want.

```bash
Metrics(mean={'toss': 2.6875}, histogram=[(0.5, {'toss': 2.0}), (0.875, {'toss': 3.0}), (0.9375, {'toss': 4.0}), (1.0, {'toss': 5.0})])
     4: 0.406250 state: {'value': '1'} / returns: {"Roll":"1"}
     5: 0.437500 state: {'value': '0'} / returns: {"Roll":"0"}
     8: 0.156250 state: {'value': '2'} / returns: {"Roll":"2"}
```

## Two Dice Problem
We previously solved the [two dice problem](/design/tutorials/performance-modeling/#simulating-two-dice-with-a-fair-coin) 
using a simpler approach that is non-optimal. It took a mean of `7.333333` tosses to generate the output.

Now, let us model the same problem using the Knuth-Yao algorithm.

For this, you just need to update the probabilities.
The probabilities for the two dice problem are `[1/36, 2/36, 3/36, 4/36, 5/36, 6/36, 5/36, 4/36, 3/36, 2/36, 1/36]`.

For this, just change the values for P, MAX_COLS and REPEATS.
```python
P = [
    '00000111',
    '00001110',
    '00010101',
    '00011100',
    '00100011',
    '00101010',
    '00100011',
    '00011100',
    '00010101',
    '00001110',
    '00000111',
    ]

MAX_COLS = 8
REPEATS = 6
```

Now, run the model checker. 

```bash
./fizz samples/knuthyaosampling/KnuthYaoSampling.fizz
Model checking samples/knuthyaosampling/KnuthYaoSampling.json
configFileName: samples/knuthyaosampling/fizz.yaml
fizz.yaml not found. Using default options
StateSpaceOptions: options:{max_actions:100  max_concurrent_actions:2}
Nodes: 70, elapsed: 22.785167ms
Time taken for model checking: 22.813916ms
Writen graph dotfile: samples/knuthyaosampling/out/run_2024-06-02_16-48-58/graph.dot
To generate svg, run: 
dot -Tsvg samples/knuthyaosampling/out/run_2024-06-02_16-48-58/graph.dot -o graph.svg && open graph.svg
Max Depth 9
PASSED: Model checker completed successfully
Writen 1 node files and 1 link files to dir samples/knuthyaosampling/out/run_2024-06-02_16-48-58
```

Now, run the performance model checker.

```bash
bazel-bin/performance/performance_bin \
    --state samples/knuthyaosampling/out/run_2024-06-02_16-48-58/  \
    --source samples/knuthyaosampling/KnuthYaoSampling.json  \
    --perf samples/knuthyaosampling/perf_model.yaml
    
Metrics(mean={'toss': 4.388888746500015}, histogram=[(0.375, {'toss': 3.0}), (0.625, {'toss': 4.0}), (0.78125, {'toss': 5.0}), (0.90625, {'toss': 6.0}), (0.9609375, {'toss': 7.0}), (0.984375, {'toss': 8.0}), (0.990234375, {'toss': 9.0}), (0.994140625, {'toss': 10.0}), (0.99658203125, {'toss': 11.0}), (0.99853515625, {'toss': 12.0}), (0.9993896484375, {'toss': 13.0}), (0.999755859375, {'toss': 14.0}), (0.999847412109375, {'toss': 15.0}), (0.999908447265625, {'toss': 16.0}), (0.9999465942382812, {'toss': 17.0}), (0.9999771118164062, {'toss': 18.0}), (0.9999904632568359, {'toss': 19.0}), (0.9999961853027344, {'toss': 20.0}), (0.999997615814209, {'toss': 21.0}), (0.9999985694885254, {'toss': 22.0}), (0.9999991655349731, {'toss': 23.0}), (0.9999996423721313, {'toss': 24.0}), (0.9999998509883881, {'toss': 25.0}), (0.9999999403953552, {'toss': 26.0})])
     8: 0.138889 state: {'value': '6'} / returns: {"Roll":"6"}
     9: 0.166667 state: {'value': '5'} / returns: {"Roll":"5"}
    10: 0.138889 state: {'value': '4'} / returns: {"Roll":"4"}
    16: 0.083333 state: {'value': '8'} / returns: {"Roll":"8"}
    17: 0.111111 state: {'value': '7'} / returns: {"Roll":"7"}
    18: 0.111111 state: {'value': '3'} / returns: {"Roll":"3"}
    19: 0.083333 state: {'value': '2'} / returns: {"Roll":"2"}
    26: 0.055556 state: {'value': '9'} / returns: {"Roll":"9"}
    27: 0.055556 state: {'value': '1'} / returns: {"Roll":"1"}
    35: 0.027778 state: {'value': '10'} / returns: {"Roll":"10"}
    36: 0.027778 state: {'value': '0'} / returns: {"Roll":"0"}
```

As you can see, compared to the simple algorithm of summing up two rolls of a dice
that took 7.33333 bits, this algorithm takes only 4.388888 bits on average.

### PRISM model checker
The Two Dice example is modelled in the PRISM model checker as well.
You can find the model at [Dice Case Study](https://www.prismmodelchecker.org/casestudies/dice.php)

As you can notice, the specification language is extremely simple with FizzBee,
in fact, the generic version of the Knuth-Yao algorithm 
is roughly the same length as the pseudo-code. Whereas the PRISM spec
is incredibly complex and will be time consuming to write and verify.

This makes FizzBee an incredible simple and easy to use alternative to PRISM.

## Conclusion
We saw how to model the Knuth-Yao algorithm in FizzBee and do probabilistic and
performance analysis automatically without any math.


