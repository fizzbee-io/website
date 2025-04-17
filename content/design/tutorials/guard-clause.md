---
title: Guard Clauses And Enabling Conditions
description: Learn how guard clauses and enabling conditions work in FizzBee to control action transitions. This guide covers testing for deadlocks, liveness, and common pitfalls—a must-read before you start writing your first model.
weight: -20
aliases:
  - "/tutorials/guard-clause/"
---

Before you do any serious modeling in any formal system, you need to understand the concept of guard clauses and enabling conditions.

Guard clauses or enabling conditions are the predicates that tell whether an action/transition is allowed or not.
Guard clauses are critical to test deadlocks and liveness properties.

Some formal methods languages like Event-B, PRISM etc use standalone guard clauses or preconditions.
FizzBee follows languages like TLA+ use embedded guard clauses where the guard is part of the action.
But unlike TLA+, FizzBee infers the enabled status of the action using a simple but unconventional set of rules.


{{< toc >}}

## Example: Simple Light Switch

{{% fizzbee %}}
action Init:
  switch = "OFF"

atomic action On:
  if switch != "ON":
    switch = "ON"

{{% /fizzbee %}}

When you run the model checker, it will show a deadlock error. Because, once the switch is turned ON,
then no other action is possible. 

Obviously, two correct ways to fix this, depending on the requirements or the expected behavior. 
1. Remove the guard clause from the `On` action. This would make, the ON action idempotent.
   That's like a elevator call button. You can press it multiple times, but it will not change the state.
   {{% fizzbee %}}
action Init:
  switch = "OFF"

atomic action On:
    switch = "ON"

   {{% /fizzbee %}}

2. Allow other actions like `Off`, that will change the state back to OFF.

{{% fizzbee %}}
action Init:
  switch = "OFF"

atomic action On:
  if switch != "ON":
    switch = "ON"

atomic action Off:
  if switch != "OFF":
    switch = "OFF"

{{% /fizzbee %}}

Instead of using if-else, you can also use `require` statements.

{{% fizzbee %}}
action Init:
  switch = "OFF"

atomic action On:
  require switch != "ON"
  switch = "ON"

atomic action Off:
  require switch != "OFF"
  switch = "OFF"

{{% /fizzbee %}}

Although if-else structure and the require statement are similar, they have some subtle differences,
that we will go over later in this doc.

## Implementation detail
In an ideal world, you probably don't need to know this. But a brief understanding of the implementation details
will help you spec the model effectively and help simplify the code and
speed up model checking.

FizzBee has multiple types of statements, similar to Python. 
One of the types is the `simple_python_stmt`, that corresponds to a subset of [Python's `simple_stmt` in this grammar](https://docs.python.org/3/reference/grammar.html).
Specifically,
- assignments (a = 1, x+=2 etc)
- star_expressions (my_list.append(1) etc)
- pass
- del (at present Python's `del` stmt is not supported, but will be added soon)
Other statements like `if-elif-else`, `for`, `any`, `while`, `return`, `continue` etc are not `simple_python_stmt`.

There is one exception for the method calls. If the method call is to builtin functions or functions in
the standard library, it is treated as `simple_python_stmt`. 
If it is a user-defined function or a fizz function, even though it is a syntactically same as
the builtin function, it is not treated as `simple_python_stmt`. Let us call it, `fizz_call_stmt`.

In many rules, this exception will be a bit annoying to learn, 
but you'll get it once you see a lot of examples.


In the atomic context, this is how the enabled status is inferred.

1. Every action starts out as disabled `action.enabled=False`.

2. For each statement that is executed, if the statement is a

   2a. `simple_python_stmt`, enable the action `action.enabled=True`.

   2b. `fizz_call_stmt` and the returned value is assigned, then enable the action `action.enabled=True`.

   2c. if `require` fails, disable the action `action.enabled=False`, and exits the action.

   2d. for any other statements, leave the enabled bit unchanged.

3. At the end of the action, if `action.enabled == True`, the action will be added to the state graph,
   and check for invariants etc.

The rules are simple and allows for an incredibly concise and expressive language.


{{% fizzbee %}}
action Init:
  switch = "OFF"

atomic action On:           # action.enabled = False
  if switch != "ON":        # UNCHANGED action.enabled irrespective of whether if is True or False
    switch = "ON"           # action.enabled = True

{{% /fizzbee %}}

If the switch is in OFF state, the ON action will be enabled only,
when the `switch = "ON"` gets executed.

If the switch is in ON state already, the action starts out disabled. 
And since the `switch = "ON"` is not executed, the action will remain disabled.

That is, the above code is equivalent to the following code.
{{% fizzbee %}}
action Init:
  switch = "OFF"

atomic action On:           # action.enabled = False
  if switch == "ON":        # UNCHANGED action.enabled irrespective of whether if is True or False
    return                  # UNCHANGED action.enabled
  switch = "ON"             # action.enabled = True
  
{{% /fizzbee %}}

Similarly, when you have if,elif,else, the action will be enabled only if at least one simple statement is executed.

{{% fizzbee %}}
action Init:
  switch = "OFF"

atomic action On:           # action.enabled = False
  if switch == "ON":        # UNCHANGED action.enabled irrespective of whether if is True or False
    return                  # UNCHANGED action.enabled
  else:                     # UNCHANGED action.enabled
    switch = "ON"           # action.enabled = True
  
{{% /fizzbee %}}

Of course, if instead of `return` if you use any statement, it will enable the action.

{{% fizzbee %}}
action Init:
  switch = "OFF"

atomic action On:           # action.enabled = False
  if switch == "ON":        # UNCHANGED action.enabled irrespective of whether if is True or False
    x = 1                   # action.enabled = True
  else:                     # UNCHANGED action.enabled
    switch = "ON"           # action.enabled = True
  
{{% /fizzbee %}}

## A possible pitfall
Although the rule is simple, some seemingly equivalent python code will not work as expected.

For example: in this example, the On action will be enabled even if it is already ON.

{{% fizzbee %}}
action Init:
    switch = "OFF"

atomic action On:               # action.enabled = False
    is_on = (switch == "ON")    # action.enabled = True
    if is_on:                   # UNCHANGED action.enabled (i.e True)
        switch = "ON"           # action.enabled = True

{{% /fizzbee %}}

The reason is, the `is_on` is a `simple_python_stmt` and it enables the action when executed.

This is a bit counter-intuitive, but it is a design choice to keep the language simple and expressive.

So, one way to still disable the action is to use `require` statement

{{% fizzbee %}}
action Init:
    switch = "OFF"

atomic action On:               # action.enabled = False
    is_on = (switch == "ON")    # action.enabled = True
    require switch != "ON"      # action.enabled = False if switch is ON and aborts the action,
                                # otherwise, UNCHANGED action.enabled
    switch = "ON"               # action.enabled = True

{{% /fizzbee %}}

In this case, when the switch is already ON, when it executes the first statement,
the action will be tentatively enabled, but the `require` statement will disable it.
And since it aborts the action, the action remains disabled.

This equally applies to `for`, `any`, `while`, function calls etc. If within a `for` loop, 
if there is at least one `simple_python_stmt` executed, the action will be enabled.

If the code calls a fizz function, and within that function there is a `simple_python_stmt` executed,
the action will be enabled.


