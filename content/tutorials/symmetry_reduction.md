---
title: Symmetry Reduction
weight: 15
---

Symmetry reduction is a technique used in model checking to reduce the state space
of a model by exploiting symmetries in the model.

{{% hint warning %}}
This works, but the document is not complete. 

{{% /hint %}}



{{< toc >}}

## Simple values for IDs
Sometimes you would want a simple value for the ID or Key.
Instead of defining the keys as strings or numbers, 
you can define them as `symmetric_values`.

{{% fizzbee %}}
# Define the keys as symmetric values instead of strings or numbers
KEYS = symmetric_values('k', 3)  # instead of KEYS = range(0, 3)

action Init:
  switches = {}
  for k in KEYS:
      switches[k] = 'OFF'
  

atomic action On:
  any k in KEYS:
    switches[k] = 'ON'

{{% /fizzbee %}}

## Symmetric Roles
Mark the role as symmetric, and the model checker will automatically
mark the symmetric transitions as equivalent.

{{% fizzbee %}}
Status = enum('INIT', 'DONE')

NUM_ROLES = 5

symmetric role Node:

  action Init:
    self.status = Status.INIT

  atomic action Done:
    self.status = Status.DONE
    done.add(self.__id__)

action Init:
  nodes = bag()
  for i in range(0, NUM_ROLES):
    nodes.add(Node())
  done = set()
{{% /fizzbee %}}

You can try it by removing the `symmetric` keyword
and see the difference in the number of states generated.

## Order independent datastructures
To reduce states explored, remember to use bags when possible instead of lists.
This will ensure, the order of operations are not relevant.
For more information on the available datastructures, see the [Datastructures](/tutorials/datastructures) tutorial.

