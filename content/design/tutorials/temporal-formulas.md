---
title: Temporal Formulas
description: "Write richer liveness and safety properties in FizzBee with temporal formulas: always, eventually, until, unless, leadsto, implies and possibly, nested freely, with no history variables."
weight: -17
---

The [liveness tutorial](/design/tutorials/liveness/) covered assertions with a single temporal
prefix: `always`, `always eventually`, `eventually always` and `exists`. Those cover most
specifications. But some requirements talk about what happens *after* something else, or *before*
it, and they don't fit a single prefix.

Temporal formulas let you combine `always`, `eventually`, `until`, `unless`, `leadsto`, `implies`
and `possibly` in one property, nested as deep as you need.

{{% toc %}}

## A loophole an invariant can't see

An airline sells basic and premium tickets:
- Basic tickets can't be refunded.
- Premium tickets get a full refund on cancel.
- A basic ticket can be upgraded to premium.

There is a loophole: buy a basic ticket, upgrade it, then cancel it for a full refund.

A first attempt at the rule is a safety invariant: no ticket is both basic and refunded.

{{% fizzbee %}}
---
deadlock_detection: false
---

action Init:
    cabin = oneof ["basic", "premium"]
    status = "booked"
    refunded = False

atomic action Upgrade:
    require status == "booked" and cabin == "basic"
    cabin = "premium"

atomic action Cancel:
    require status == "booked"
    status = "cancelled"
    if cabin == "premium":
        refunded = True

atomic action Fly:
    require status == "booked"
    status = "flown"

always assertion NoBasicRefund:
    return not (cabin == "basic" and refunded)
{{% /fizzbee %}}

It passes. By the time the ticket is refunded it is premium, so no single state looks wrong. The bug is
in the *history*: the ticket started as basic.

Without temporal formulas, the usual fix is a history variable that remembers the original cabin, added
to the model only so an assertion can read it. With a formula, say what you mean instead: once a ticket
is basic, it is never refunded, whatever happens next.

```python
assertion BasicNeverRefunded:
    return always (cabin == "basic" implies always not refunded)
```

Add it to the spec and run it again. It fails, and the counterexample is the loophole:

```
Any:cabin="basic"   {"cabin":"basic","refunded":false,"status":"booked"}
Upgrade             {"cabin":"premium","refunded":false,"status":"booked"}
Cancel              {"cabin":"premium","refunded":true,"status":"cancelled"}
```

## Writing a formula assertion

A formula assertion is an `assertion` with **no prefix**. Its body may compute locals and call
functions like any assertion, and it ends with one `return` of a formula:

```python
assertion StaysStarted:
    return always (started implies always started)
```

The prefixed forms you already know are special cases. These two are the same check:

```python
always eventually assertion Idle:
    return busy == 0

assertion Idle:
    return always eventually busy == 0
```

Keep using the prefixed forms for simple properties. Reach for a formula when the property needs more
than one temporal operator.

### Operators

| FizzBee | Holds on a run when | LTL | TLA+ |
|---|---|---|---|
| `always P` | P holds in every state | □P, G P | `[]P` |
| `eventually P` | P holds in some state, now or later | ◇P, F P | `<>P` |
| `P until Q` | Q holds in some state, and P in every state before it | P U Q | |
| `P unless Q` | P holds until Q holds, or forever if Q never does | P W Q | |
| `P leadsto Q` | every state where P holds is followed, now or later, by one where Q holds | □(P → ◇Q) | `P ~> Q` |
| `P implies Q` | P is false or Q holds | P → Q | `P => Q` |
| `not`, `and`, `or` | as usual | ¬, ∧, ∨ | `~`, `/\`, `\/` |
| `possibly P` | some path from this state reaches a state where P holds | CTL's EF P | |

Each part of the formula without a temporal operator, like `cabin == "basic"`, is an ordinary
expression, evaluated in every state. There is no "next" operator: a formula can't tell a state from a
repeat of it.

## Properties that start from a condition

The airline property has a shape you will use often:

```python
always (Precondition implies Property)
```

It checks `Property` from every state where `Precondition` holds. `Property` can be anything:

| You want | Write |
|---|---|
| Once P, Q stays true | `always (P implies always Q)` |
| Once P, Q never happens | `always (P implies always not Q)` |
| Once P, Q eventually happens | `always (P implies eventually Q)`, or `P leadsto Q` |
| Once P, Q is still reachable | `always (P implies possibly Q)` |
| Once P, P holds until Q | `always (P implies (P unless Q))` |

## Responses: leadsto

The most common liveness requirement is a response: every request is eventually answered. With
prefixed assertions, you would need to track which requests are open. With `leadsto` it is one line.

{{% fizzbee %}}
---
deadlock_detection: false
---

NUM_CLIENTS = 2

action Init:
    started = False
    pending = [False] * NUM_CLIENTS
    answered = [0] * NUM_CLIENTS

atomic fair action Start:
    require not started
    started = True

atomic action Request:
    require started
    c = oneof [i for i in range(NUM_CLIENTS) if not pending[i] and answered[i] < 2]
    pending[c] = True

atomic fair action Respond:
    c = oneof [i for i in range(NUM_CLIENTS) if pending[i]]
    pending[c] = False
    answered[c] += 1

func no_requests():
    return True not in pending

# No request arrives before the server starts, and it does start.
assertion NoRequestsBeforeStart:
    return no_requests() until started

# A client has at most one pending request, and it is eventually answered.
assertion Answered for c in range(NUM_CLIENTS):
    return pending[c] leadsto not pending[c]

# Once started, the server stays started.
assertion StaysStarted:
    return always (started implies always started)
{{% /fizzbee %}}

Like every liveness property, `leadsto` depends on [fairness](/design/tutorials/liveness/#fairness).
Remove `fair` from `Respond` and `Answered[0]` fails: a run can leave a request pending forever.

`Respond` picks a client with a plain `oneof`, so it could keep answering the same client. That can't
starve the other one here, because each client sends at most two requests: once one client is done,
`Respond` has only the other left to pick. Without that bound you'd need a `fair oneof` as well, as
described in [choice fairness](/design/tutorials/liveness/#choice-oneof-fairness).

`leadsto` is satisfied at once when Q already holds in the same state as P. Q doesn't have to become
true later.

## Ordering: until and unless

`P until Q` says P holds in every state up to the one where Q holds, **and Q does happen**. That is the
strong until of LTL.

Often you don't want to require Q. A lease is held until it is handed back, but a client may keep it
forever. That is `unless`, the weak until: P holds until Q, or forever if Q never happens.

{{% fizzbee %}}
---
deadlock_detection: false
---

action Init:
    leased = False
    returned = False
    renewals = 0

atomic action Take:
    require not leased and not returned
    leased = True

atomic fair action Renew:
    require leased and renewals < 2
    renewals += 1

atomic action Return:
    require leased
    leased = False
    returned = True

# Once taken, the lease stays held until it is handed back, or forever.
assertion HeldUntilReturned:
    return always (leased implies (leased unless returned))

# The lease is never handed back before it is taken.
assertion NotReturnedBeforeTaken:
    return (not returned) unless leased
{{% /fizzbee %}}

Change the second `unless` to `until` and it fails: `Take` isn't fair, so a run may never take the lease.

A bare `P unless Q` or `P until Q` is checked from the first state only. To check it from every state
where P starts, wrap it as `always (start implies (P unless Q))`.

## Can versus will: possibly

All the operators above are about what *will* happen on every fair run. Sometimes the requirement is
about what *can* happen: from any booked state, the customer can still cancel. Nothing forces them to,
so `eventually cancelled` would fail.

`possibly P` holds in a state when some path from it, of zero or more steps, reaches a state where P
holds. The path may take any action, fair or not, but never a crash: recovery that needs a fault isn't
something a user can count on.

{{% fizzbee %}}
---
deadlock_detection: false
---

action Init:
    status = "none"
    upgraded = False

atomic fair action Book:
    require status == "none"
    status = "booked"

atomic fair action Cancel:
    require status == "booked"
    status = "cancelled"

atomic fair action Rebook:
    require status == "cancelled"
    status = "none"

atomic fair<strong> action Fly:
    require status == "booked"
    status = "flown"

atomic action Upgrade:
    require status == "booked" and not upgraded
    upgraded = True

# From every booked state, cancelling is still possible.
assertion CanCancel:
    return always (status == "booked" implies possibly status == "cancelled")

# Upgrade isn't fair, so `eventually upgraded` would fail. But it can happen.
assertion CanUpgrade:
    return always ((status == "booked" and not upgraded) implies possibly upgraded)

# Once flown, booking is no longer possible.
assertion FlyingIsFinal:
    return always (status == "flown" implies not possibly status == "booked")
{{% /fizzbee %}}

A few things to know:
- `always possibly P` is a recoverability check: from every reachable state, the system can still get
  to P. It is the multi-step version of [`next_states()`](/reference/language/assertions/), which looks
  only one step ahead.
- What follows `possibly` is a condition on a state. `possibly (always P)` is an error.
- `exists eventually P` is another spelling of `possibly P`.
- When a formula with `possibly` fails, the report says after which step of the counterexample the
  condition became unreachable.

## One property per value

Often you want the same property for each client, key or ticket. A `for` clause on the header checks
one instance per value, and reports each one by name, like `Answered[0]` and `Answered[1]`:

```python
assertion Answered for c in range(NUM_CLIENTS):
    return pending[c] leadsto not pending[c]
```

Clauses can be nested and filtered, take tuples, and also work on prefixed assertions:

```python
always eventually assertion Copied for k in KEYS for r in REPLICAS if r != PRIMARY:
    return r in copies[k]

assertion StaysCopied for k, r in WATCHED:
    return always (r in copies[k] implies always r in copies[k])
```

The iterables and filters may use only constants and builtins: they are evaluated once, before `Init`.
They can't iterate over symmetric values yet.

## Calling functions in assertions

Inside an assertion, fizz `func`s can be called anywhere in an expression, including inside a
formula and in list comprehensions:

```python
role Consumer:
    func done():
        return self.received == MAX_MESSAGES

func all_done():
    return all([c.done() for c in consumers])

assertion Finishes:
    return eventually always all_done()
```

Each call runs on its own copy of the state, so it can't change the model. It must be deterministic:
no `oneof`, `any` or parallel blocks. Outside assertions, fizz function calls still have to be
[standalone statements](/design/tutorials/limitations/).

## Pitfalls

**Add parentheses around the operand of a prefix operator.** `always x >= 0 and y >= 0` would mean
`(always x >= 0) and y >= 0`, so FizzBee rejects it. Write `always (x >= 0 and y >= 0)`.

**`implies`, `until`, `unless` and `leadsto` don't chain.** Write `(P until Q) until R`, not
`P until Q until R`. The same for `(a leadsto b) and (c leadsto d)`.

**Locals are recomputed in every state.** A local is a definition, not a snapshot:

```python
assertion Grows:
    v = counter
    return eventually counter > v    # compares counter with itself: always false
```

To compare against a fixed value, use a `for` clause over the values instead:

```python
assertion Grows for v in range(MAX):
    return always (counter == v implies eventually counter > v)
```

**One return, at the end.** A formula can't be chosen with `if`. Use separate assertions, or move the
condition into a local or into the formula itself.

## Common patterns

For a request that is made and then served:

| Pattern | Formula |
|---|---|
| Invariance | `always (served implies requested)` |
| Existence | `eventually served` |
| Response | `requested leadsto served` |
| Precedence | `(not served) unless requested` |
| Stays true | `always (served implies always served)` |
| Stability | `eventually always served` |
| Recurrence | `always eventually served` |
| Constrained response | `always (requested implies (requested until served))` |
| Conditional | `(always eventually requested) implies (always eventually served)` |
| Reachability | `always possibly idle` |

## Limits

- Formulas are checked by the default (strict) liveness checker, not with `liveness: eventual`,
  in simulation mode or with `--experimental_no_graph`.
- An assertion has at most 64 distinct conditions; each use of `possibly` counts as one more.
- There is no next operator and no release operator. `P R Q` is `Q unless (P and Q)`.

The full rules, including operator precedence, are in the
[language reference](/reference/language/assertions/). The reference examples `09-14` to `09-21` in the
[FizzBee repository](https://github.com/fizzbee-io/fizzbee/tree/main/examples/references) are small,
runnable versions of everything on this page.
