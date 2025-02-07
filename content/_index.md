---
Title: FizzBee – Design Reliable, Scalable Distributed Systems
Description: Designing a distributed system? FizzBee makes it easy to model, visualize, and
  validate your design—catching flaws before you code. The easiest-ever formal methods,
  built for developers.
geekdocNav: true
geekdocAlign: center
geekdocAnchor: false
geekdocBreadcrumb: false
---
# Find bugs before you code
FizzBee is a design specification language and model checker to specify distributed systems
at a much higher level of abstraction than a programming language for system analysis and design.

Automatically analyze and find design issues like 

consistency, fault tolerance, data corruption  
performance, latency, availability and a lot more.

{{< button size="large" relref="tutorials/getting-started/" >}}Get Started{{< /button >}}

{{< columns >}}

### Exhaustive model checking

Explore all possible behaviors and exhaustive set of complex
interactions and verify the system does what you think it does.

<--->

### Easiest specification language

FizzBee uses Python-like language, using imperative style. You can be
productive in minutes.

<--->

### Performance modeling

FizzBee comes with probabilistic model checker for modeling performance characteristics like 
expected latency, throughput, availability SLAs.

{{< /columns >}}

## Try Fizz

Read the [quick start guide](/tutorials/getting-started/) to learn how to write your first FizzBee model
or comb through the [examples](/examples/)
or tinker with the [FizzBee online playground](/play)


{{% fizzbee %}}
# Fizzbee model checker

invariants:
  always value <= 3  # This statement is always true
  always eventually value == 0  # The value can be anything, but always come back to 0
  eventually always value >= 0  # The value will reach 0 eventually, and stay >= 0


action Init:
  value = -2


atomic fair action Add:
  if value < 3:
      value += 1
  else:
      value = 0

{{% /fizzbee %}}



