---
title: Getting Started
description: Learn how to use FizzBee's Model Based Testing to test your Go code.
weight: -20
geekdocHidden: true
---

Model-based testing with FizzBee is simple and intuitive — if you can describe how your system should behave, FizzBee can generate the tests automatically.

A basic familiarity with the FizzBee specification language is helpful. If you haven’t seen it yet, we recommend a quick look at the [Getting Started with FizzBee](../getting-started/) guide. The syntax is mostly Python-like, and even a brief skim will make the examples here easier to follow.

This guide currently shows examples in **Go**. Guides for **Java** and **Rust** are coming soon.

{{% toc %}}

## Introduction
Explain model based testing, and prerequisites

## Installation
FizzBee's model based testing is released separately from the FizzBee's model checker.

**On Mac with homebrew:**, 
```bash
# If you haven't installed fizzbee yet
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

## Basic Concepts

Before we dive into testing, let’s get familiar with a few core ideas that model-based testing with FizzBee relies on.
I'd recommend skimming the [Getting Started with FizzBee](../getting-started/) guide if you haven't already.

### Model
A **model** is a high-level description of how your system behaves — essentially a **state machine** that captures possible states and transitions. In FizzBee, you define this model using the FizzBee specification language.

### Roles
**Roles** represent the components of your system — such as services, databases, or background processes.  
They are similar to **classes** in object-oriented programming: each role defines its own state and the actions it can perform.

### Actions
**Actions** are the operations (like functions) that change the state of the system. They describe how your system transitions from one state to another.  
Actions can be defined **within a role** (e.g., a database write operation) or as **global actions** (e.g., a cluster-wide failover event).

### Non-deterministic Choices
Real-world systems often behave differently depending on inputs, timing, or concurrent events. 
FizzBee models the non-deterministic inputs with **non-deterministic choices**, expressed using the `any` keyword.

For example:
```fizzbee
key = any SET_OF_AVAILABLE_KEYS
```
This means the model will try every possible key from the given set, helping tests explore a wide range of scenarios.

The other types of non-determinism will be introduced as we go along.

## Mapping model to implementation
To test your actual code against the model, you need to connect the two. This is done through a **refinement mapping**.

It is like describing how your code implements the design. There are two main parts to this:

1. **Action Mapping:**

  Define how each action in the model corresponds to a method or function in your code. In the model,
  you might have an action like `Put`, but in a real implementation in a specific language and framework, 
  the name and parameters could be significantly different. They would also accept additional parameters like 
  context, request metadata, timeouts, retry strategy and more etc.

  So, we need a way to map the abstract actions in the model to the concrete methods in the code.

  In FizzBee's model based testing, the action mapping is done by implementing the `Adapter` interface.
  This is required for testing.

2. **State Mapping:**

  Define how the abstract state variables in your model correspond to the actual state in your code. 
  For example, a key-value store in the implementation might be represented as a simple map/dictionary in the model.
  It is specified by implementing the `StateGetter` or `SnapshotStateGetter` interface. Specifying the 
  state mapping is mostly optional, but highly recommended to catch more violations quickly. In some cases,
  where the model doesn't have any getter actions, specifying the state mapping is required.



## Adapter interface

Roles interface, Action methods, The Arg parameter etc. Explain the mapping.

## Explain the benefit of StateGetter and SnapshotStateGetter and when to use these

## Better representative example