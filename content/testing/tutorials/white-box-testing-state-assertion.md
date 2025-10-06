---
title: White box testing - State assertion
description: State assertion is a white-box testing technique that involves verifying the internal state of a system to ensure it behaves as expected.
    State assertions can find bugs quicker and make debugging easier and sometimes that black-box testing cannot even find.
weight: 0

---

{{< toc >}}

## Why white-box testing?

In the quick start guide, we saw how to use FizzBee's model-based testing to generate tests that verify 
the external behavior of a system. This is known as black-box testing, 
where the internal workings of the system are not considered.

However, sometimes we want to verify the internal state of the system as well.
This is known as white-box testing, where we have access to the internal state and can make assertions about it.

Some examples when white-box testing is useful:
- Performance optimizations that do not change the external behavior but change the internal state. For example, caching, lazy loading,
  inserting data in a sorted order and using binary search instead of linear search, and so on.
- Complex algorithms where the internal state is important to verify. For example, a sorting algorithm, a graph algorithm, and so on.
- Many times, if a bug is found, it is easier to debug if we can see the internal state of the system. Because, the consequence of a bug might be farther away from the cause.

In this tutorial, we will see how to use state assertions in FizzBee to verify the internal state of a system.


## Starter Code
We will use the same counter example from the [Quick Start](../quick-start/) guide.
Follow the quick start instructions at least until the section [Minimal implementation to pass the tests - attempt 1](../quick-start/#minimal-implementation-to-pass-the-tests---attempt-1).

{{% expand "Starter code for the counter_adaptor.go for this guide" %}}
Most likely, you would have completed the full quick start guide and would have gone well past it. So, I have provided the starter code for the `counter_adaptor.go` file here.

```go
// Generated scaffold by fizzbee-mbt generator
// Source: ../specs/simple-counter/counter.fizz
// Update the methods with your implementation.
package counter

import (
	mbt "github.com/fizzbee-io/fizzbee/mbt/lib/go"
)

// Role adaptors

// CounterRoleAdapter is a stub adaptor for CounterRole
type CounterRoleAdapter struct {
	count int
}

// Assert that CounterRoleAdapter satisfies CounterRole
var _ CounterRole = (*CounterRoleAdapter)(nil)

func (a *CounterRoleAdapter) ActionInc(args []mbt.Arg) (any, error) {
	a.count++
	return nil, nil
}

func (a *CounterRoleAdapter) ActionGet(args []mbt.Arg) (any, error) {
	return a.count, nil
}

func (a *CounterRoleAdapter) ActionDec(args []mbt.Arg) (any, error) {
	// TODO: implement action Dec
	return nil, mbt.ErrNotImplemented
}

// Model adaptor
type CounterModelAdapter struct {
	counterRole *CounterRoleAdapter
}

// Assert that CounterModelAdapter satisfies CounterModel
var _ CounterModel = (*CounterModelAdapter)(nil)

// Constructor for CounterModelAdapter
func NewCounterModel() CounterModel {
	return &CounterModelAdapter{}
}

func GetTestOptions() map[string]any {
	return map[string]any{
		"max-seq-runs":      1000,
		"max-parallel-runs": 0,
		"max-actions":       20,
	}
}

func (m *CounterModelAdapter) GetState() (map[string]any, error) {
	// TODO: implement GetState. Required.
	return nil, mbt.ErrNotImplemented
}

func (m *CounterModelAdapter) GetRoles() (map[mbt.RoleId]mbt.Role, error) {
	roles := map[mbt.RoleId]mbt.Role{
		{RoleName: "Counter", Index: 0}: m.counterRole,
	}
	return roles, nil
}

func (m *CounterModelAdapter) Init() error {
	m.counterRole = &CounterRoleAdapter{}
	return nil
}

func (m *CounterModelAdapter) Cleanup() error {
	// TODO: implement Cleanup
	return nil
}
```
{{% /expand %}}

Here, the `Inc` would increment the counter unconditionally. So, 
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

### Wrong fix: Add a limit at Get()
In the above example, the test failed because the model expected the counter to be 3, but the actual value was 5.
One way to fix it, is to add a limit at the `Get` method.
```go {linenos=table,linenostart=25,hl_lines=[2,3,4]}
func (a *CounterRoleAdapter) ActionGet(args []mbt.Arg) (any, error) {
    if a.count > 3 {
        return 3, nil
    }
    return a.count, nil
}
```
Now, run the tests again.
```bash
go test ./fizztests 
ok  	fizzbee-mbt-quickstart/fizztests	1.450s
```

The tests passed. But, this is not the correct fix. Because, as of now, the observed behavior of the counter is the same as the model,
while the implementation is not correct. The counter can go beyond 3, but the `Get` method is hiding it.

The issue will be observable only when the `Dec` method is implemented. Or it reaches maximum integer value and overflows, that most won't test anyway.

## State assertion
One way to catch this issue earlier is to use state assertions.
That is, after an `Inc()` check if the internal state is as expected.

To do this in FizzBee, the role adaptor needs to implement either the `StateGetter` interface or
`SnapshotStateGetter` interface.
```go
// StateGetter is an interface for roles that can return their current state.
// When implemented, test can use these to assert the next state of the role.
// If both GetState() and SnapshotState() methods are implemented, SnapshotState takes precedence.
type StateGetter interface {
	// GetState returns the current state without guaranteeing thread safety.
	GetState() (map[string]any, error)
}

// SnapshotStateGetter is an interface for roles that can return a consistent snapshot of their state.
// When implemented, this method would be used concurrently with the role's actions, to test the intermediate states.
// Sometimes, implementing these would be hard, so it is not required but recommended.
// If both GetState() and SnapshotState() methods are implemented, SnapshotState takes precedence.
type SnapshotStateGetter interface {
	// SnapshotState returns a consistent, concurrency-safe snapshot of the state.
	SnapshotState() (map[string]any, error)
}
```

This table summarizes how these two interfaces are used.

| StateGetter     | SnapshotStateGetter | Sequential Tests               | Parallel Tests |
|-----------------|---------------------|--------------------------------|----------------|
| Not Implemented | Not Implemented     | Not used                       | Not used       |
| Implemented     | Not Implemented     | Yes                            | Not used       |
| Not Implemented | Implemented         | Yes                            | Yes            |
| Implemented     | Implemented         | Yes (SnapshotStateGetter used) | Yes            |

In our case, we can implement the `StateGetter` interface in the `CounterRoleAdapter`.

```go {linenos=table,linenostart=12,hl_lines=[3,4,5,6,7]}
// GetState implements mbt.StateGetter.
func (a *CounterRoleAdapter) GetState() (map[string]any, error) {
	return map[string]any{
		"value": a.count,
	}, nil
}
```
Now, run the tests again.
```bash {hl_lines=[2,4,6]}
go test ./fizztests --max-actions=4
Validation failed: Failed: Role Counter#0, field 'value', 
expected: 
int_value:3
actual: 
int_value:4
      0: Counter#0.Inc()
      1: Counter#0.Inc()
      2: Counter#0.Inc()
==>   3: Counter#0.Inc()
Test failure after 50 trace(s).
To retry the same trace, use: --seq-seed=1759770652580860000
2025/10/06 10:10:52 Runner exited with error: exit status 1
2025/10/06 10:10:52 exit status 1
FAIL	fizzbee-mbt-quickstart/fizztests	0.242s
FAIL
```

Now, you can see, we were able to catch the issue. Here, the bug is visible where it actually happens,
making debugging easier.

Without the state assertion, the only time we would have seen the issue is when the `Dec` method is implemented and tested.
The shortest trace would be `Inc(), Inc(), Inc(), Inc(), Dec(), Get()`, which is 6 actions long.

### Correct fix: Limit at Inc()
The correct fix is to add the limit at the `Inc` method as in the quick start guide.

