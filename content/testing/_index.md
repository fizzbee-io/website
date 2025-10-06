---
title: "Model-Based Testing"
description: "Autonomous, concurrency-aware testing for complex systems. Test incrementally, keep your source clean, and catch concurrency bugs early."

weight: -10
---

### Autonomous, concurrency-aware testing for complex stateful systems

---

## Why Model-Based Testing?
Hand-written test cases don’t scale. As systems grow more stateful and concurrent, it becomes impossible to anticipate every edge case. Most testing completely misses concurrency issues.

With **Model-based testing (MBT)**, instead of writing tests, you define *how your system should behave*. FizzBee then generates and runs lots and lots of scenarios, automatically checking your implementation against the model.

It’s like property-based testing for **stateful, concurrent systems**.

---

## How It Works
1. **Define the model** — Describe valid operations and rules for your system in FizzBee's python-like state machine language.
2. **Generate scenarios** — FizzBee autonomously explores sequences of actions and interleavings.
3. **Refinement mapping** — Connect the code to the design - defining how the code implements the design by implementing a adapter interface.
4. **Run Tests** — FizzBee Test Runner tests your system extensively including concurrent behavior and reports any violations.

---

## Why FizzBee MBT is Different

- **Concurrency-Aware**  
  FizzBee systematically explores interleavings, catching subtle race conditions that other MBT tools miss.

- **Clean Source Code**  
  No intrusive tracing libraries or logging calls; test logic is fully isolated from your code.

- **Incremental Testing**  
  Test as you build. Unimplemented features can be marked and ignored, so new code is validated immediately. This enables true test-driven development, without having to write tests.

- **Truly Autonomous**  
  Unlike AI-written tests, FizzBee requires **no manual review** of generated cases. Tests are deterministic, reproducible, and mathematically rigorous — with no fragile edits when your code changes.

- **Replayable Failures**  
  Every bug comes with a minimal, reproducible trace for fast debugging.

---

## Benefits at a Glance

✅ Catch concurrency bugs early  
✅ Test incrementally during development (true TDD for stateful systems)  
✅ Keep source code clean and uncluttered  
✅ Validate against formal models, not scattered assertions  
✅ Build confidence faster in complex, distributed software

---

## Use Cases

- Distributed databases and storage systems
- APIs and microservices with evolving state
- Concurrent services where order of operations matters
- Any stateful system too complex for hand-written test suites

---

## Build Confidence Faster

FizzBee MBT lets you focus on **what the system should do**, not how to manually test it.  
Define the rules once. Let FizzBee do the rest.

👉 [Get Started with Model-Based Testing](tutorials/quick-start/)  
