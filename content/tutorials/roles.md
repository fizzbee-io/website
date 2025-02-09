---
title: Actors / Roles
description: "Roles are a core concept in FizzBee, simplifying how we model system participants like microservices, processes, and threads. Learn how to define roles, manage state, handle communication, and model dynamic behaviors."
weight: 10
---

Roles are like classes in object oriented programming. They have states and actions.
But here, they may represent a participant in a system. It could be a, 
- microservice
- process
- thread
- just a role (Eg. coordinator, participant in 2-Phase Commit)
- database

If you are writing a design doc, and created a block diagram with it,
they most likely represent a role in the system.

Roles can have state, actions, functions and even assertions like
a top level spec. So basically, roles just provide a way to organize the code.


{{< toc >}}

## Role

Role is just a collection of states, actions and functions.

The syntax should be familiar to most python programmers.
The state variables will be initialized in the `Init` action,
and the variables can be accessed using `self` reference.
(Java and other languages use `this` instead of `self`)

To initialize, just call the constructor with the role name.


{{% fizzbee %}}
Status = enum('INIT', 'DONE')

role Node:

  action Init:
    self.status = Status.INIT

  action Done:
    self.status = Status.DONE

action Init:
  n = Node()

{{% /fizzbee %}}

Run it in the FizzBee playground, you can see the two possible states, and the graph.


## Parameters

You can pass in arguments to the role constructor as named parameters.
The parameters will be automatically assigned to the role variables.

For example, you can assign a unique id to a role instance.

{{% fizzbee %}}
Status = enum('INIT', 'DONE')

role Node:

  action Init:
    self.status = Status.INIT

  atomic action Done:
    self.status = Status.DONE
    done.add(self.NAME)

action Init:
  n1 = Node(NAME=1)
  n2 = Node(NAME=2)
  done = set()

{{% /fizzbee %}}

Now, notice the NAME is available as self.NAME. You can set multiple parameters as needed.

### Unique ID for each role instance
Roles have a unique ID assigned to them, which can be accessed using `self._id__`.

{{% fizzbee %}}
Status = enum('INIT', 'DONE')
NUM_ROLES = 3
role Node:

  action Init:
    self.status = Status.INIT

  atomic action Done:
    self.status = Status.DONE
    done.add(self.__id__)

action Init:
  nodes = []
  for i in range(0, NUM_ROLES):
    nodes.append(Node())
  done = set()

{{% /fizzbee %}}

## Symmetric Roles
See [Symmetric Roles](/tutorials/symmetry_reduction/#symmetric-roles) for more details
on symmetry reduction and how it applies to roles.

## Functions
Again, like in the top level spec, you can define functions in the role.

{{% fizzbee %}}
Status = enum('INIT', 'DONE')

role Node:

  action Init:
    self.status = Status.INIT

  atomic action Done:
    self.done()

  atomic func done():
    self.status = Status.DONE
    done.add(self.NAME)

action Init:
  n1 = Node(NAME=1)
  n2 = Node(NAME=2)
  done = set()

{{% /fizzbee %}}

## Dynamic Role Creation and Deletion

You can create and delete roles dynamically. When a role is created, 
from the next yield point on, the actions would be automatically scheduled.

Similarly, when a role is deleted, the actions would be removed from the scheduler.

{{% fizzbee %}}
MIN_NODES=1
MAX_NODES=2

Status = enum('INIT', 'DONE')

role Node:

  action Init:
    self.status = Status.INIT

  atomic action Done:
    self.status = Status.DONE
    done.add(self.ID)


action Init:
  nodes = []
  for i in range(0, MIN_NODES):
      n = Node(ID=i)
      nodes.append(n)
  done = set()

atomic action AddNode:
  if len(nodes) < MAX_NODES:
    n = Node(ID=len(nodes))
    nodes.append(n)

atomic action RemoveNode:
  nodes = nodes[0:len(nodes)-1]

{{% /fizzbee %}}

## Role Communication
Read more about [Role Communication](/tutorials/channels/)

## Example: Two Phase Commit with actor style
Take a look at the [2-Phase Commit example](/examples/two_phase_commit_actors/) for
a more complex example of roles in action.
