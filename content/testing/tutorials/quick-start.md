---
title: Quick Start
description: Learn how to use FizzBee's Model Based Testing to test your Go code.
weight: -20

---

This is a quick start guide to get you up and running with FizzBee's Model Based Testing for Go.
Quick start guide for Java and Rust are coming soon.`
We'll cover additional details and more complex examples in later documents.

In this guide, we'll cover:
- Installing FizzBee and FizzBee-MBT
- Create and validate a simple FizzBee model
- Implement test adapter in Go.
- Test Driven Development (TDD) workflow without writing a single test.
- Test single threaded and multi-threaded behavior.
- Integration test with an external database.
- Checking code coverage of the tests.

**Table of Contents**
{{% toc %}}

## Install FizzBee and FizzBee-MBT

FizzBee has two components: 
- the FizzBee model checker for validating the system design
- the FizzBee Model Based Testing (MBT) tool to test your implementation.

**On Mac with homebrew:**,
```bash
brew tap fizzbee-io/fizzbee
brew install fizzbee

brew tap fizzbee-io/fizzbee-mbt
brew install fizzbee-mbt
```
**Manual installation**

Alternatively, you can download and install them manually. You'll need both the FizzBee Model Checker and the FizzBee Model Based Testing binaries.

For FizzBee Model Checker, the binaries are available at,
https://github.com/fizzbee-io/fizzbee/releases

For FizzBee Model Based Testing, the binaries are available at,
https://github.com/fizzbee-io/fizzbee-mbt-releases/releases

Make sure to add both the un-tarred (`tar -xzf filename.tar.gz`) directories to your PATH.

## Start a new Go project
Most likely you will use FizzBee-MBT in an existing project. 
But for this quick start guide, let's create a new Go project.

```bash
# cd to a directory where you want to create the project.
mkdir fizzbee-mbt-quickstart
cd fizzbee-mbt-quickstart
go mod init fizzbee-mbt-quickstart

```

## Write a FizzBee model

In most projects, we would keep the model in a separate directory under `specs` or `models` directory.

```bash
mkdir -p specs/simple-counter
vim specs/simple-counter/counter.fizz  # Or any editor of your choice
```

{{% fizzbee %}}
# counter.fizz
#
# A simple counter that can be incremented and decremented
# Inc and Dec will be a no-op after value reaches the MAX or 0 respectively

MAX = 3
role Counter:
    action Init:
        self.value = 0

    atomic action Inc:
        if self.value < MAX:
            self.value += 1
        else:
            # with explicit pass, Inc becomes a NoOp after it reaches MAX
            # without the pass, Inc will be considered disabled after it reaches MAX
            pass

    atomic action Get:
        return self.value

    atomic action Dec:
        if self.value > 0:
            self.value -= 1
        else:
            pass

action Init:
    counter = Counter()

always assertion WithinRange:
    # return counter.value >= 0 and counter.value <= MAX
    return counter.value in range(0, MAX+1)

{{% /fizzbee %}}

### Run the model checker in the playground
You could run and explore the model with the FizzBee online playground at https://fizzbee.io/play

Run the above code in the playground.
"Run in playground" will open the snippet in the playground.
Then, click "Enable whiteboard" checkbox and click Run.
{{< figure src="https://storage.googleapis.com/fizzbee-public/website/tutorials/img/EnableWhiteboardAndRun.png" alt="Enable whiteboard and Run" caption="The screenshot of the playground highlighting the Enable whiteboard and Run steps" >}}

When you run it, you'll see an `Explorer` link. Click you'll see an explorer.
{{< figure src="https://storage.googleapis.com/fizzbee-public/website/tutorials/img/ClickExplorerLink.png" alt="Click Explorer Link to open the Explorer view" caption="The screenshot of the playground highlighting the Explorer link to open the Explorer view" >}}

## Run the model checker locally
For model based testing, you'll need to run the model checker locally.
```bash
fizz specs/simple-counter/counter.fizz
```
The output states would be stored in a directory `specs/simple-counter/out/run_<timestamp>`.

## Generate the test skeleton
Now, run the scaffolding command to generate the test skeleton and the adapter code.
```bash
fizz mbt-scaffold  \
        --lang go \
        --go-package counter \
        --gen-adapter \
        --out-dir fizztests/ \
        specs/simple-counter/counter.fizz
```
Optionally, format the generated code with `go fmt` for consistent code style.
```bash
go fmt fizztests/*
```

This will generate 3 files under `fizztests` directory. 

| File                  | Description                                                    | Edit/Implement |
|-----------------------|----------------------------------------------------------------|----------------|
| counter_test.go       | The test starter code that can be started with `go test`.      | Do not edit    |
| counter_interfaces.go | The interfaces for the roles and actions defined in the model. | Do not edit    |
| counter_adapters.go   | The scaffolding for the adapter implementing the interface.    | Implement      |

Take a quick look at the `counter_interfaces.go` file and the `counter_adapters.go`.

{{% expand "Overview of the generated files" %}}
Each model has a single model interface. The name matches the model name in the spec.
Our model is simple, and it doesn't have any top level actions. So, the model interface is empty.
```go
// Model interface for the whole specification
type CounterModel interface {
    mbt.Model
}
```
The mbt.Model interface defines a few methods. `Init` equivalent to the `action Init` where you initialize
anything needed for the model's Init and test setup. and `Cleanup` is equivalent to tearDown functions of many xUnit frameworks.

For each role defined, there is a corresponding role interface. Our CounterRole has a few actions.
```go
type CounterRole interface {
    mbt.Role
    ActionInc(args []mbt.Arg) (any, error)
    ActionGet(args []mbt.Arg) (any, error)
    ActionDec(args []mbt.Arg) (any, error)
}
```
{{% /expand %}}

## Implement the adapter

### Get the fizzbee-mbt package
First step, you'll need to `go get` the fizzbee-mbt package.
```bash
go get github.com/fizzbee-io/fizzbee/mbt/lib/go
```

### Run the tests to see the failures
FizzBee MBT runs with two processes. 
- fizzbee-mbt-server does the validation.
- FizzBee MBT test runner runs the tests.

In one terminal, run the server.
Use this path to the states file from the model checker output.
```bash
fizzbee-mbt-server --states_file specs/simple-counter/out/run_2025-09-26_14-15-41 > /tmp/server.log
```
The output will be something like this.
```bash
2025/09/26 15:05:26 Loaded 8 nodes and 24 links
2025/09/26 15:05:26 State Space Options: options:{max_actions:100 max_concurrent_actions:2 crash_on_yield:true} deadlock_detection:true
2025/09/26 15:05:26 FizzMo server listening on :50051
```

In another terminal, run the tests `go test ./fizztests`.
```bash
go test ./fizztests 
2025/09/26 15:11:22 Init RPC returned error: Failed to get roles: not implemented
2025/09/26 15:11:22 Init failed: Init failed: Failed to get roles: not implemented
2025/09/26 15:11:22 Runner exited with error: exit status 1
2025/09/26 15:11:22 exit status 1
FAIL	fizzbee-mbt-quickstart/fizztests	0.353s
FAIL
```
The test fails because we haven't implemented the adapter yet.

### Implement GetRoles method
Open the `fizztests/counter_adapters.go` file. And look for the `GetRoles` method.
```go {linenos=table,linenostart=57}
func (m *CounterModelAdapter) GetRoles() (map[mbt.RoleId]mbt.Role, error) {
	// TODO: implement GetRoles. Required.
	return nil, mbt.ErrNotImplemented
}
```
For the test runner to invoke the actions on the roles, it needs to know what roles are there. This is the critical
step in the adapter implementation.
In our model, there is a single instance of the Counter. So, we need to return a map with a single entry.

```go {linenos=table,linenostart=57}
func (m *CounterModelAdapter) GetRoles() (map[mbt.RoleId]mbt.Role, error) {
	roles := map[mbt.RoleId]mbt.Role{
		{RoleName: "Counter", Index: 0}: /* fix this*/,
	}
	return roles, nil
}
```
So, to finally fix, this. Make these 3 changes.
1. Add a field `counterRole` of type `*CounterRoleAdapter` to the `CounterModelAdapter` struct.
```go {linenos=table,linenostart=34,hl_lines=[2]}
type CounterModelAdapter struct {
    counterRole *CounterRoleAdapter
}
```
2. Initialize the field in the `Init` method.
```go {linenos=table,linenostart=66,hl_lines=[2]}
func (m *CounterModelAdapter) Init() error {
	m.counterRole = &CounterRoleAdapter{}
	return nil
}
```
3. Return the field in the `GetRoles` method.
```go {linenos=table,linenostart=59,hl_lines=[3]}
func (m *CounterModelAdapter) GetRoles() (map[mbt.RoleId]mbt.Role, error) {
    roles := map[mbt.RoleId]mbt.Role{
        {RoleName: "Counter", Index: 0}: m.counterRole,
    }
    return roles, nil
}
```

Now, run the tests again.
```bash
go test ./fizztests 
ok  	fizzbee-mbt-quickstart/fizztests	1.985s
```

The tests passed. Even though we don't have an implementation. 

Before we work it out, let's try verbose logging to see what's happening. adding `-v` flag to `go test`.
```bash
go test -v ./fizztests 
=== RUN   TestCounter
Sequential tests succeeded! Number of sequential runs: 1000
Parallel tests succeeded! Number of parallel runs: 1000
2025/09/27 14:24:48 Test executor shut down gracefully.
--- PASS: TestCounter (1.81s)
PASS
ok  	fizzbee-mbt-quickstart/fizztests	1.812s
```
Here, you can see, FizzBee tried 1000 sequential and 1000 parallel runs.

So why didn't the tests fail?
It is because,
we haven't implemented the actions yet, and the default implementation for the actions
return `mbt.ErrNotImplemented` error. (For Java, it will throw ActionNotImplementedException)
FizzBee treats actions that return `mbt.ErrNotImplemented` as disabled tests.
 
{{% expand "Why tests don't fail when actions are not implemented?" %}}

One of the design goals of FizzBee Model Based Testing is to be a replacement for manually written tests.
When you are developing a new feature, you do not have the full implementation ready. But fizzbee can 
generate exhaustive tests for the feature you are working on.
That means, the tests will fail everytime until your development is complete. During the development phase,
the developers will not run these tests, and so usually they will write tests manually, wasting developer's time.
And they won't realize FizzBee's full benefits.

As and when you implement the actions, the tests will start failing for real issues.
{{% /expand %}}

### Sequential tests
In the adapter file, there is a `GetTestOptions` method with this default implementation.
```go {linenos=table,linenostart=46}
func GetTestOptions() map[string]any {
	return map[string]any{
		"max-seq-runs":      1000,
		"max-parallel-runs": 1000,
		"max-actions":       20,
	}
}
```
For now, let's disable the parallel tests. We will explore parallel tests in a later document.
```go {linenos=table,linenostart=46,hl_lines=[4]}
func GetTestOptions() map[string]any {
    return map[string]any{
        "max-seq-runs":      1000,
        "max-parallel-runs": 0,    // disable parallel tests for now
        "max-actions":       20,
    }
}
```

#### Try the first failure - Get and Inc action

In fizztests/counter_adapters.go, implement the `ActionGet` method in `CounterModelAdapter`.

**Replace this code:**
```go {linenos=table,linenostart=23}
func (a *CounterRoleAdapter) ActionGet(args []mbt.Arg) (any, error) {
	// TODO: implement action Get
	return nil, mbt.ErrNotImplemented
}
```
**With this code:**
```go {linenos=table,linenostart=23,hl_lines=[2]}
func (a *CounterRoleAdapter) ActionGet(args []mbt.Arg) (any, error) {
	return 0, nil
}
```
Similarly, implement the `ActionInc` method.
```go {linenos=table,linenostart=18,hl_lines=[2]}
func (a *CounterRoleAdapter) ActionInc(args []mbt.Arg) (any, error) {
    return nil, nil
}
```

Now, run `go test ./fizztests` again.
```bash
go test ./fizztests 
Validation failed: Failed: Counter#0.Get, expected: [int_value:2], actual: [int_value:0]
      0: Counter#0.Inc()
      1: Counter#0.Inc()
==>   2: Counter#0.Get() -> 0
Return value mismatched
Expected:
      2: Counter#0.Get() -> 2
Test failure after 1 trace(s).
To retry the same trace, use: --seq-seed=1759010359241424000
2025/09/27 14:59:19 Runner exited with error: exit status 1
2025/09/27 14:59:19 exit status 1
FAIL	fizzbee-mbt-quickstart/fizztests	0.257s
FAIL
```

You'll see a trace something like the above. FizzBee tries various sequence of actions, until the first failure.
In this case, it tried two `Inc` actions followed by a `Get` action. So, the expected value is 2, but our `Get` action always returns 0.

{{% hint %}}
When you run, you might see a different trace. That is because, FizzBee explores the state space randomly.
You can execute the same trace again by using the `--seq-seed` option with the seed value shown in the output.

At present, FizzBee MBT does not implement shrinking. So, the trace might be longer than the minimal trace. You can find shorter traces by
passing `--max-actions` option with a smaller value. For example, `--max-actions=2`.

```bash
go test ./fizztests --max-actions=2
Validation failed: Failed: Counter#0.Get, expected: [int_value:1], actual: [int_value:0]
      0: Counter#0.Inc()
==>   1: Counter#0.Get() -> 0
Return value mismatched
Expected:
      1: Counter#0.Get() -> 1
Test failure after 20 trace(s).
To retry the same trace, use: --seq-seed=1759010533300160000
2025/09/27 15:02:13 Runner exited with error: exit status 1
2025/09/27 15:02:13 exit status 1
FAIL	fizzbee-mbt-quickstart/fizztests	0.270s
FAIL
```
{{% /hint %}}

#### Minimal implementation to pass the tests - attempt 1
Let us try a minimal implementation to pass the tests. Just add a counter field to the adapter struct.

In most implementations, you probably will have a separate Counter struct that has the state and methods.
The adapter will just call the methods on the struct. But for simplicity, we will keep everything in the adapter struct.

```go {linenos=table,linenostart=13,hl_lines=[2]}
type CounterRoleAdapter struct {
	count int
}
```
Then, fill in the methods.
```go {linenos=table,linenostart=20,hl_lines=[2,7]}
func (a *CounterRoleAdapter) ActionInc(args []mbt.Arg) (any, error) {
	a.count++
	return nil, nil
}

func (a *CounterRoleAdapter) ActionGet(args []mbt.Arg) (any, error) {
	return a.count, nil
}
```
Now, run the tests again.
```bash
go test ./fizztests 
Validation failed: Failed: Counter#0.Get, expected: [int_value:3], actual: [int_value:5]
      0: Counter#0.Inc()
      1: Counter#0.Get() -> 1
      2: Counter#0.Inc()
      3: Counter#0.Inc()
      4: Counter#0.Inc()
      5: Counter#0.Inc()
==>   6: Counter#0.Get() -> 5
Return value mismatched
Expected:
      6: Counter#0.Get() -> 3
Test failure after 22 trace(s).
To retry the same trace, use: --seq-seed=1759020910396258000
2025/09/27 17:55:10 Runner exited with error: exit status 1
2025/09/27 17:55:10 exit status 1
FAIL	fizzbee-mbt-quickstart/fizztests	0.282s
FAIL
```
In our model, the counter has a maximum value of 3. So, the `Inc` action should be a no-op after it reaches 3.

You might be able to reproduce the smallest trace above with `--max-actions=5` option.

#### Fixing the boundary condition - attempt 2
```go {linenos=table,linenostart=20,hl_lines=[2,3,4]}
func (a *CounterRoleAdapter) ActionInc(args []mbt.Arg) (any, error) {
    if a.count < 3 {
        a.count++
    }
    return nil, nil
}
```

Now run the tests again.
```bash
go test ./fizztests    
ok  	fizzbee-mbt-quickstart/fizztests	1.410s
```

The tests passed! Try running with `-v` flag to see the number of runs.
```bash
=== RUN   TestCounter
Sequential tests succeeded! Number of sequential runs: 1000
Parallel tests succeeded! Number of parallel runs: 0
2025/09/27 18:19:37 Test executor shut down gracefully.
--- PASS: TestCounter (1.22s)
PASS
ok  	fizzbee-mbt-quickstart/fizztests	1.438s
```
The tests passed. You have successfully implemented the adapter for the simple counter model.
For the sequential tests, FizzBee tried 1000 different sequences of actions.

### Parallel tests
Now, let's enable the parallel tests by setting `max-parallel-runs` to a non-zero value.
```go {linenos=table,linenostart=49,hl_lines=[4]}
func GetTestOptions() map[string]any {
    return map[string]any{
        "max-seq-runs":      1000,
        "max-parallel-runs": 10000,    // enable parallel tests
        "max-actions":       20,
    }
}
```

Run it again.
```bash
go test ./fizztests                 
Sequential tests succeeded! Number of sequential runs: 1000
                                  1: START Counter#0.Inc()
                                  1: END  
  0: START Counter#0.Inc()
  0: END  
                                  1: START Counter#0.Inc()
                                  1: END  
                                  1: START Counter#0.Get()
                                  1: END  2
                                  1: START Counter#0.Get()
                                  1: END  2
                                  1: START Counter#0.Inc()
                                  1: END  
                                  1: START Counter#0.Inc()
                                  1: END  
Validation failed: Validation failed
Wrote validate request to /tmp/fizzmo-validate-req-3170371744.json
Test failure after 2789 trace(s).
To retry the same trace, use: --parallel-seed=1759023986695434000
2025/09/27 18:46:26 Runner exited with error: exit status 1
2025/09/27 18:46:26 exit status 1
FAIL	fizzbee-mbt-quickstart/fizztests	2.688s
FAIL
```
This is a random attempt. You might see a different trace. If it passes, you might have to run multiple times.
But with Go, there is a better way to find concurrency bugs. Read the next section.

If it fails, you will see a trace like the above. The trace shows interleaved actions from two parallel runs.
It is a bit hard to read. FizzBee uses porcupine for checking linearizability of concurrent operations. You can see
the generated trace by opening the trace visualization at
```bash
open /tmp/fizzbee-porcupine.html
```

You might see something like,

{{< rawhtml>}}
<iframe width="100%" height="180" srcdoc='
<html><head>
    <meta charset="UTF-8">
    <title>Porcupine</title>
    <style>
      html {
  font-family: Helvetica, Arial, sans-serif;
  font-size: 16px;
}

text {
dominant-baseline: middle;
}

#legend {
position: fixed;
left: 10px;
top: 10px;
background-color: rgba(255, 255, 255, 0.5);
backdrop-filter: blur(3px);
padding: 5px 2px 1px 2px;
border-radius: 4px;
}

#canvas {
margin-top: 45px;
}

#calc {
width: 0;
height: 0;
visibility: hidden;
}

.bg {
fill: transparent;
}

.divider {
stroke: #ccc;
stroke-width: 1;
}

.history-rect {
stroke: #888;
stroke-width: 1;
fill: #42d1f5;
}

.client-annotation-rect {
stroke: #888;
stroke-width: 1;
fill: #e0e0e0;
}

.link {
fill: #206475;
cursor: pointer;
}

.selected {
stroke-width: 5;
}

.target-rect {
opacity: 0;
}

.history-text {
font-size: 0.9rem;
font-family:
Menlo,
Courier New,
monospace;
}

.hidden {
opacity: 0.2;
}

.hidden line {
opacity: 0.5; /* note: this is multiplicative */
}

.linearization {
stroke: rgba(0, 0, 0, 0.5);
}

.linearization-invalid {
stroke: rgba(255, 0, 0, 0.5);
}

.linearization-point {
stroke-width: 5;
}

.linearization-line {
stroke-width: 2;
}

.tooltip {
position: absolute;
display: none;
width: max-content;
max-width: 300px;
border: 1px solid #ccc;
background: white;
border-radius: 4px;
padding: 5px;
font-size: 0.8rem;
}

.inactive {
display: none;
}

    </style>
  </head>
  <body>
    <div id="legend">
      <svg xmlns="http://www.w3.org/2000/svg" width="660" height="20">
        <text x="0" y="10">Clients</text>
        <line x1="50" y1="0" x2="70" y2="20" stroke="#000" stroke-width="1"></line>
        <text x="70" y="10">Time</text>
        <line x1="110" y1="10" x2="200" y2="10" stroke="#000" stroke-width="2"></line>
        <polygon points="200,5 200,15, 210,10" fill="#000"></polygon>
        <rect x="300" y="5" width="10" height="10" fill="rgba(0, 0, 0, 0.5)"></rect>
        <text x="315" y="10">Valid LP</text>
        <rect x="400" y="5" width="10" height="10" fill="rgba(255, 0, 0, 0.5)"></rect>
        <text x="415" y="10">Invalid LP</text>
        <text x="520" y="10" id="jump-link" class="link">[ jump to first error ]</text>
      </svg>
    </div>
    <div id="canvas"><svg width="1135.8671875" height="95"><g><rect height="95" width="1135.8671875" x="0" y="0" class="bg"></rect><text x="28.8984375" y="25" text-anchor="end">0</text><text x="28.8984375" y="70" text-anchor="end">1</text><line x1="38.8984375" y1="10" x2="38.8984375" y2="85" class="divider"></line></g><g><g><rect height="30" width="150.046875" x="208.9453125" y="10" rx="4" ry="4" class="history-rect" style=""></rect><text x="283.96875" y="25" text-anchor="middle" class="history-text" style="">Counter#0.Inc()</text></g><g><rect height="30" width="150.046875" x="38.8984375" y="55" rx="4" ry="4" class="history-rect" style=""></rect><text x="113.921875" y="70" text-anchor="middle" class="history-text" style="">Counter#0.Inc()</text></g><g><rect height="30" width="150.046875" x="208.9453125" y="55" rx="4" ry="4" class="history-rect" style=""></rect><text x="283.96875" y="70" text-anchor="middle" class="history-text" style="">Counter#0.Inc()</text></g><g><rect height="30" width="193.390625" x="378.9921875" y="55" rx="4" ry="4" class="history-rect" style=""></rect><text x="475.6875" y="70" text-anchor="middle" class="history-text" style="">Counter#0.Get() -&gt; 2</text></g><g><rect height="30" width="193.390625" x="592.3828125" y="55" rx="4" ry="4" class="history-rect" style=""></rect><text x="689.078125" y="70" text-anchor="middle" class="history-text" style="">Counter#0.Get() -&gt; 2</text></g><g><rect height="30" width="150.046875" x="805.7734375" y="55" rx="4" ry="4" class="history-rect" style=""></rect><text x="880.796875" y="70" text-anchor="middle" class="history-text" style="">Counter#0.Inc()</text></g><g><rect height="30" width="150.046875" x="975.8203125" y="55" rx="4" ry="4" class="history-rect" style=""></rect><text x="1050.84375" y="70" text-anchor="middle" class="history-text" style="">Counter#0.Inc()</text></g></g><g></g><g><line x1="38.8984375" x2="38.8984375" y1="50" y2="90" class="linearization linearization-point"></line><line x1="38.8984375" x2="208.9453125" y1="50" y2="45" class="linearization linearization-line"></line><line x1="208.9453125" x2="208.9453125" y1="5" y2="45" class="linearization linearization-point"></line><line x1="208.9453125" x2="228.9453125" y1="45" y2="50" class="linearization linearization-line"></line><line x1="228.9453125" x2="228.9453125" y1="50" y2="90" class="linearization linearization-point"></line><line x1="228.9453125" x2="378.9921875" y1="50" y2="50" class="linearization-invalid linearization-line"></line><line x1="378.9921875" x2="378.9921875" y1="50" y2="90" class="linearization-invalid linearization-point"></line></g><g><rect height="30" width="150.046875" x="208.9453125" y="10" class="target-rect" data-partition="0" data-index="0"></rect><rect height="30" width="150.046875" x="38.8984375" y="55" class="target-rect" data-partition="0" data-index="1"></rect><rect height="30" width="150.046875" x="208.9453125" y="55" class="target-rect" data-partition="0" data-index="2"></rect><rect height="30" width="193.390625" x="378.9921875" y="55" class="target-rect" data-partition="0" data-index="3"></rect><rect height="30" width="193.390625" x="592.3828125" y="55" class="target-rect" data-partition="0" data-index="4"></rect><rect height="30" width="150.046875" x="805.7734375" y="55" class="target-rect" data-partition="0" data-index="5"></rect><rect height="30" width="150.046875" x="975.8203125" y="55" class="target-rect" data-partition="0" data-index="6"></rect></g></svg><div class="tooltip" style="display: none;"></div></div>
    <div id="calc"><svg><text text-anchor="end">1</text></svg></div>



</body></html>'>
</iframe>
{{< /rawhtml >}}

You could see, the concurrency issue. An Inc() from another thread was ignored.

#### Go Race Detector

Go comes with a great tool called [Data Race Detector](https://go.dev/doc/articles/race_detector). You can enable it by passing `-race` flag to `go test`.

```bash
go test -race ./fizztests
```
It will print a lot of stack trace. The interesting part is at the top.
```bash
==================
WARNING: DATA RACE
Write at 0x00c0005a1038 by goroutine 22044:
  fizzbee-mbt-quickstart/fizztests.(*CounterRoleAdapter).ActionInc()
      src/fizzbee-mbt-examples/examples/fizzbee-mbt-quickstart/fizztests/counter_adapters.go:22 +0x50
  fizzbee-mbt-quickstart/fizztests.init.func1()
      src/fizzbee-mbt-examples/examples/fizzbee-mbt-quickstart/fizztests/counter_test.go:18 +0x9c
  github.com/fizzbee-io/fizzbee/mbt/lib/go.(*FizzBeeMbtPluginServer).executeCommand()
      src/fizzbee/mbt/lib/go/plugin_service.go:320 +0xb4
  github.com/fizzbee-io/fizzbee/mbt/lib/go.(*FizzBeeMbtPluginServer).executeSequence()
      src/fizzbee/mbt/lib/go/plugin_service.go:207 +0x78
  github.com/fizzbee-io/fizzbee/mbt/lib/go.(*FizzBeeMbtPluginServer).executeSequencesConcurrent.func1()
      src/fizzbee/mbt/lib/go/plugin_service.go:230 +0x5c
  golang.org/x/sync/errgroup.(*Group).Go.func1()
      go/pkg/mod/golang.org/x/sync@v0.16.0/errgroup/errgroup.go:93 +0x7c

Previous read at 0x00c0005a1038 by goroutine 22043:
  fizzbee-mbt-quickstart/fizztests.(*CounterRoleAdapter).ActionGet()
      src/fizzbee-mbt-examples/examples/fizzbee-mbt-quickstart/fizztests/counter_adapters.go:28 +0x2c
  fizzbee-mbt-quickstart/fizztests.init.func2()
      src/fizzbee-mbt-examples/examples/fizzbee-mbt-quickstart/fizztests/counter_test.go:21 +0x9c
  github.com/fizzbee-io/fizzbee/mbt/lib/go.(*FizzBeeMbtPluginServer).executeCommand()
      src/fizzbee/mbt/lib/go/plugin_service.go:320 +0xb4
  github.com/fizzbee-io/fizzbee/mbt/lib/go.(*FizzBeeMbtPluginServer).executeSequence()
      src/fizzbee/mbt/lib/go/plugin_service.go:207 +0x78
  github.com/fizzbee-io/fizzbee/mbt/lib/go.(*FizzBeeMbtPluginServer).executeSequencesConcurrent.func1()
      src/fizzbee/mbt/lib/go/plugin_service.go:230 +0x5c
  golang.org/x/sync/errgroup.(*Group).Go.func1()
      go/pkg/mod/golang.org/x/sync@v0.16.0/errgroup/errgroup.go:93 +0x7c
```

Let's look at the first location.
```go {linenos=table,linenostart=20,hl_lines=[3]}
func (a *CounterRoleAdapter) ActionInc(args []mbt.Arg) (any, error) {
	if a.count < 3 {
		a.count++
	}
	return nil, nil
}
```
and the second location.
```go {linenos=table,linenostart=27,hl_lines=[2]}
func (a *CounterRoleAdapter) ActionGet(args []mbt.Arg) (any, error) {
	return a.count, nil
}
```
That is, both are accessing the `count` field concurrently without synchronization.

#### Fixing the concurrency issue

Let's fix it by adding a mutex to the adapter struct.
```go {hl_lines=[2]}
type CounterRoleAdapter struct {
	mu    sync.Mutex
	count int
}
```
And use the mutex in the methods.
```go {hl_lines=[2,3,11,12]}
func (a *CounterRoleAdapter) ActionInc(args []mbt.Arg) (any, error) {
	a.mu.Lock()
	defer a.mu.Unlock()
	if a.count < 3 {
		a.count++
	}
	return nil, nil
}

func (a *CounterRoleAdapter) ActionGet(args []mbt.Arg) (any, error) {
	a.mu.Lock()
	defer a.mu.Unlock()
	return a.count, nil
}
```

Now run the tests again.
```bash
go test -race ./fizztests
ok  	fizzbee-mbt-quickstart/fizztests	15.123s
```

## Exercises (with solutions)

### Exercise 1: Enable the Dec action with a dummy implementation and see tests fail
In the model, there is a Dec action. But we haven't implemented it yet.
Implement a dummy implementation that does nothing and see the tests fail.

{{% expand "Solution" %}}
```go
func (a *CounterRoleAdapter) ActionDec(args []mbt.Arg) (any, error) {
    // Dummy implementation
    return nil, nil
}
```

Run the tests again.
```bash
go test -race ./fizztests 
Validation failed: Failed: Counter#0.Get, expected: [int_value:0], actual: [int_value:1]
      0: Counter#0.Get() -> 0
      1: Counter#0.Inc()
      2: Counter#0.Dec()
==>   3: Counter#0.Get() -> 1
Return value mismatched
Expected:
      3: Counter#0.Get() -> 0
Test failure after 1 trace(s).
To retry the same trace, use: --seq-seed=1759025876947872000
2025/09/27 19:17:56 Runner exited with error: exit status 1
2025/09/27 19:17:56 exit status 1
FAIL	fizzbee-mbt-quickstart/fizztests	0.328s
FAIL
```
{{% /expand %}}

### Exercise 2: Implement the Dec action to pass the sequential tests
Implement the Dec action to pass the sequential tests. 
{{% hint %}}
Tip: You can temporarily disable without removing the parallel tests by passing `--max-parallel-runs=0` flag.
{{% /hint %}}

{{% expand "Solution" %}}
```go
func (a *CounterRoleAdapter) ActionDec(args []mbt.Arg) (any, error) {
    if a.count > 0 {
        a.count--
    }
    return nil, nil
}
```
Now run the tests again.
```bash
go test ./fizztests  --max-parallel-runs=0
ok  	fizzbee-mbt-quickstart/fizztests	4.831s
```
{{% /expand %}}

### Exercise 3: Run only the parallel tests (and disable sequential tests)
Tip: You can disable sequential tests by passing `--max-seq-runs=0` flag.

{{% expand "Solution" %}}
```bash
go test -race ./fizztests  --max-seq-runs=0
```
{{% /expand %}}

### Exercise 4: Fix the concurrency issue in Dec action
Implement the Dec action to pass the parallel tests.

{{% expand "Solution" %}}
You have already added the mutex to the struct. So, just use it in the Dec action.
```go {hl_lines=[2,3]}
func (a *CounterRoleAdapter) ActionDec(args []mbt.Arg) (any, error) {
    a.mu.Lock()
    defer a.mu.Unlock()
    if a.count > 0 {
        a.count--
    }
    return nil, nil
}
```
Now run the tests again.
```bash
go -race test ./fizztests  --max-seq-runs=0
ok  	fizzbee-mbt-quickstart/fizztests	15.456s
```
{{% /expand %}}

## Refactor: Using a separate Counter struct
So far, we kept everything in the adapter struct for simplicity. But in a real implementation, you will be testing a real Counter usually in
a different package. Most likely, you will be testing an existing code. Either as a library,
or as a service through its API - either REST API or gRPC.
Also, the counter might be persisted in a database or a shared cache like redis.

For this example, let us refactor the code to use a separate Counter struct.

file: `./mem_counter.go`
```go
type MemCounter struct {
	mu sync.Mutex
	// limit is the maximum value of the counter
	limit int
	// value is the current value of the counter
	value int
}

// NewMemCounter creates a new MemCounter with the given limit.
func NewMemCounter(limit int) *MemCounter {
	return &MemCounter{limit: limit}
}

```

Implement the methods - Inc, Dec, and Get.
{{% expand "Solution: Method implementations" %}}
```go
func (c *MemCounter) Inc() {
	c.mu.Lock()
	defer c.mu.Unlock()
	if c.value < c.limit {
		c.value++
	}
}
func (c *MemCounter) Dec() {
	c.mu.Lock()
	defer c.mu.Unlock()
	if c.value > 0 {
		c.value--
	}
}
func (c *MemCounter) Get() int {
	c.mu.Lock()
	defer c.mu.Unlock()
	return c.value
}
```
{{% /expand %}}

Now, modify the adapter to use the MemCounter struct.
file: `./fizztests/counter_adapters.go`

{{% expand "Solution: Adapter code using the MemCounter struct" %}}
```go {linenos=table,linenostart=15,hl_lines=[2]}
type CounterRoleAdapter struct {
	counter *simplecounter.MemCounter
}
```
Initialize the adapter in the `Init` method.
```go {linenos=table,linenostart=69,hl_lines=[3]}
func (m *CounterModelAdapter) Init() error {
	m.counterRole = &CounterRoleAdapter{
		counter: simplecounter.NewMemCounter(3),
	}
	return nil
}
```
{{% /expand %}}

Update the action methods to call the methods on the MemCounter struct.
{{% expand "Solution: Action methods calling MemCounter methods" %}}
```go {linenos=table,linenostart=22,hl_lines=[2,7,11]}
func (a *CounterRoleAdapter) ActionInc(args []mbt.Arg) (any, error) {
	a.counter.Inc()
	return nil, nil
}

func (a *CounterRoleAdapter) ActionGet(args []mbt.Arg) (any, error) {
	return a.counter.Get(), nil
}

func (a *CounterRoleAdapter) ActionDec(args []mbt.Arg) (any, error) {
	a.counter.Dec()
	return nil, nil
}
```
{{% /expand %}}

### Exercise 5: Create a PostgresCounter struct that implements the same methods

{{% expand "Solution: PGCounter" %}}

1. Start the postgres database. (If you haven't installed it, just use docker for now)
```bash
docker run --rm --name my-postgres -e POSTGRES_PASSWORD=mysecretpassword -p 5432:5432 -d postgres
```
2. Connect to the instance and create a table.
```bash
docker exec -it my-postgres psql -U postgres
```
3. Create a database table to store the counter state.
```sql
CREATE TABLE counters (
    name TEXT PRIMARY KEY,
    value INT NOT NULL,
    max INT NOT NULL
);
```
4. Implement the PGCounter struct in a new file `pg_counter.go`.

file: pg_counter.go
```go
package simplecounter

import (
    "context"
    "database/sql"
    "errors"
    "fmt"
)

type PGCounter struct {
    db   *sql.DB
    name string
    max  int
}

// NewPGCounter initializes or fetches an existing counter with the given name.
func NewPGCounter(ctx context.Context, db *sql.DB, name string, max int) (*PGCounter, error) {
    // Try to insert the counter; if it already exists, do nothing.
    _, err := db.ExecContext(ctx, `
        INSERT INTO counters (name, value, max)
        VALUES ($1, 0, $2)
        ON CONFLICT (name) DO NOTHING
    `, name, max)
    if err != nil {
        return nil, fmt.Errorf("failed to init counter: %w", err)
    }

    return &PGCounter{db: db, name: name, max: max}, nil
}

// update performs the delta update (+1 or -1) safely with max checks.
func (c *PGCounter) update(ctx context.Context, delta int) error {
    tx, err := c.db.BeginTx(ctx, nil)
    if err != nil {
        return err
    }
    defer tx.Rollback() // Safe to call even after commit.

    var value, max int
    err = tx.QueryRowContext(ctx, `
        SELECT value, max
        FROM counters
        WHERE name = $1
        FOR UPDATE
    `, c.name).Scan(&value, &max)
    if err != nil {
        return fmt.Errorf("fetch counter state: %w", err)
    }

    newValue := value + delta
    if newValue < 0 || newValue > max {
        return errors.New("counter update out of bounds")
    }

    _, err = tx.ExecContext(ctx, `
        UPDATE counters
        SET value = $1
        WHERE name = $2
    `, newValue, c.name)
    if err != nil {
        return fmt.Errorf("update counter: %w", err)
    }

    return tx.Commit()
}

func (c *PGCounter) Inc(ctx context.Context) error {
    return c.update(ctx, 1)
}

func (c *PGCounter) Dec(ctx context.Context) error {
    return c.update(ctx, -1)
}

func (c *PGCounter) Get(ctx context.Context) (int, error) {
    var value int
    err := c.db.QueryRowContext(ctx, `
        SELECT value
        FROM counters
        WHERE name = $1
    `, c.name).Scan(&value)
    if err != nil {
        return 0, fmt.Errorf("get counter: %w", err)
    }
    return value, nil
}

func (c *PGCounter) Close() error {
    return c.db.Close()
}

func (c *PGCounter) DeleteCounter() error {
    _, err := c.db.ExecContext(context.Background(), `
        DELETE FROM counters
        WHERE name = $1
    `, c.name)
    return err
}

```
5. Fix the adapter to use PGCounter instead of MemCounter.
file: `./fizztests/counter_adapters.go`
```go {hl_lines=[2]}
type CounterRoleAdapter struct {
	counter *simplecounter.PGCounter
}
```
Fix the methods to pass context and handle errors.
```go {hl_lines=[2,3]}
func (a *CounterRoleAdapter) ActionInc(args []mbt.Arg) (any, error) {
	err := a.counter.Inc(context.Background())
	return nil, err
}
// similarly for Dec and Get
```

Create the db connection in the Init method.
```go

func (m *CounterModelAdapter) Init() error {
	ctx := context.Background()
	db, err := sql.Open("postgres", "postgres://postgres:mysecretpassword@localhost:5432/postgres?sslmode=disable")
	if err != nil {
		return err
	}
	counter, err := simplecounter.NewPGCounter(ctx, db, "counter-"+uuid.New().String(), 3)
	if err != nil {
		return err
	}
	m.counterRole = &CounterRoleAdapter{
		counter: counter,
	}
	return nil
}
```
Implement the Cleanup method to close the db connection and delete counter.
```go
func (m *CounterModelAdapter) Cleanup() error {
	if m.counterRole != nil {
		m.counterRole.counter.DeleteCounter()
		m.counterRole.counter.Close()
	}
	return nil
}
```

{{% /expand %}}

## Checking Code Coverage
You can check the code coverage of your tests by passing `-coverprofile` flag to `go test`.
```bash
go test -race -count=1 -coverprofile ./coverage.out -coverpkg=./ ./fizztests
ok  	fizzbee-mbt-quickstart/fizztests	327.110s	coverage: 82.8% of statements in ./
```
Then generate the HTML report.
```bash
go tool cover -html=coverage.out
```

### Wrap up
Congratulations! You have completed the FizzBee MBT quickstart tutorial. 
In this tutorial, you have learned how to create a model, implement the adapter, run sequential and parallel tests,
and check code coverage. You can now apply these skills to test your own applications using FizzBee MBT.
