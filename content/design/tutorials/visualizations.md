---
title: Whiteboard Visualizations
weight: 30
description: "Automatically generate sequence diagrams, state diagrams, and algorithm animations from simple pseudo code. Explore every state and transition interactively, ensuring your algorithms meet all requirements with zero extra effort."

aliases:
  - "/tutorials/visualizations/"
---

FizzBee generates multiple visualizations and diagrams. So far you would have seen,
automatically generated state diagrams. In addition to state diagrams, FizzBee also
generates sequence diagrams and algorithm visualizations.

These are helpful in understanding the algorithm and the system behavior. 


{{% toc %}}

| **Feature**                  | **Description**                                                                                                                                              |
|------------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **Pseudo Code to Visualizations** | Generates sequence, state, and algorithm diagrams directly from high-level, Python-like pseudo code.                                                                 |
| **Zero Extra Effort**        | Visualizations are created directly from your pseudo code with no additional manual input required.                                                          |
| **Interactive Experience**   | Provides a dynamic, whiteboard-like interface to explore states, transitions, and scenarios in real time.                                                    |
| **Comprehensive Simulation** | Automatically simulates complex scenarios like non-atomic operations, crashes, message loss, concurrency, and visualizes all possible states.                |
| **Correctness Assertion**    | Enables adding assertions to ensure the design meets safety and liveness requirements.                                                                       |
| **Easy to Use**              | Familiar Python-like syntax reduces the learning curve compared to other formal methods tools.                                                               |

## Enable whiteboard visualizations
On the fizzbee playground, you can enable the whiteboard visualizations by setting
the `Enable Whiteboard` checkbox. Then click `Run` button. 

Once the model checking is done, you can see a link to the `Explorer` in the `Console`.

Clicking on the `Explorer` link will open the explorer in a new tab.

## Example 1: Two phase commit
Before we go over the tutorial, let's see a complete working example.

1. Open the [Two Phase Commit](/examples/two_phase_commit_actors/#complete-code) example
in the play ground

{{< expand "Show fizzbee spec for Two Phase Commit" >}}
For the detailed explanation of the spec, see [Two Phase Commit](/examples/two_phase_commit_actors/)
Click 'Run in playground'

{{< fizzbee >}}

NUM_PARTICIPANTS = 2

role Coordinator:

  action Init:
    self.prepared = set()
    self.state = "init"

  action Write:
    if self.state != "init":
      return
    self.state = "working"
    for rm in self.PARTICIPANTS:
      vote = rm.Prepare()

      if vote == 'aborted':
        self.Abort()
        return

      self.prepared.add(rm.ID)
    
    self.Commit()


  fair action Timeout:
    if self.state != "committed":
      self.Abort()

  fair action Restart:
    if self.state == "committed":
      for rm in self.PARTICIPANTS:
        rm.Commit()

  func Abort():
      self.state = "aborted"
      for rm in self.PARTICIPANTS:
          rm.Abort()

  func Commit():
    if self.state == 'working' and len(self.prepared) == len(self.PARTICIPANTS):
      self.state = 'committed'
      for rm in self.PARTICIPANTS:
        rm.Commit()


role Participant:
  action Init:
    self.state = "working"

  fair action Timeout:
    if self.state == "working":
      self.state = "aborted"

  func Prepare():
    if self.state != 'working':
      return self.state
    oneof:
      self.state = 'prepared'
      self.state = 'aborted'
    return self.state

  func Commit():
    self.state = 'committed'

  func Abort():
    self.state = 'aborted'


always assertion ResMgrsConsistent:
  for rm1 in participants:
    for rm2 in participants:
      if rm1.state == 'committed' and rm2.state == 'aborted':
        return False
  return True

eventually always assertion Terminated:
  return coordinator.state in ('committed', 'aborted')


action Init:
  participants = []
  for i in range(NUM_PARTICIPANTS):
    p = Participant(ID=i)
    participants.append(p)

  coordinator = Coordinator(PARTICIPANTS=participants)

{{< /fizzbee >}}

{{< /expand >}}

2. Enable `Enable Whiteboard` checkbox, and Run. 
3. Once the model checker completes, click on `Communication Diagram` link in the console.
   This will show the block diagram for the two phase commit protocol.
    {{% graphviz %}}
digraph G {
  node [shape=box];
  splines=false;
  rankdir=LR;
  "Participant" [shape=none label=<<table cellpadding="14" cellspacing="8" style="dashed">
      <tr><td port="p0">Participant#0</td></tr>
      <tr><td port="p1" border="0">&#x022EE;</td></tr>
      <tr><td port="p2">Participant#2</td></tr>
      </table>>]
  "Coordinator" -> "Participant":p0 [label="Prepare, Abort, Commit"];
  "Coordinator" -> "Participant":p2 [label="Prepare, Abort, Commit"];
  "FairActionParticipant" [shape=none label=<<table cellpadding="14" cellspacing="8" style="invisible"><tr>
      <td port="Timeout"></td>
      </tr></table>>]
  { rank=same; "Participant"; "FairActionParticipant"; }
  "FairActionParticipant":Timeout -> "Participant" [label="Timeout"];
  "actionCoordinatorWrite" [label="" shape="none"]
  "actionCoordinatorWrite" -> "Coordinator" [label="Write"];
  "FairActionCoordinator" [shape=none label=<<table cellpadding="14" cellspacing="8" style="invisible"><tr>
      <td port="Timeout"></td>
      <td port="Restart"></td>
      </tr></table>>]
  { rank=same; "Coordinator"; "FairActionCoordinator"; }
  "FairActionCoordinator":Timeout -> "Coordinator" [label="Timeout"];
  "FairActionCoordinator":Restart -> "Coordinator" [label="Restart"];
}
    {{% /graphviz %}}
4. Click on the `Explorer` link in the console.
5. You would see the Init state of the system 
   {{% graphviz %}}
   digraph G {
   compound=true;
   subgraph "cluster_Participant#0" {
   style=dashed;
   label="Participant#0";
   "Participant#0_placeholder" [label="" shape=point width=0 height=0 style=invis];
   "Participant#0.state" [label="state = working" shape=ellipse];
   }
   subgraph "cluster_Participant#1" {
   style=dashed;
   label="Participant#1";
   "Participant#1_placeholder" [label="" shape=point width=0 height=0 style=invis];
   "Participant#1.state" [label="state = working" shape=ellipse];
   }
   subgraph "cluster_Coordinator#0" {
   style=dashed;
   label="Coordinator#0";
   "Coordinator#0_placeholder" [label="" shape=point width=0 height=0 style=invis];
   subgraph "cluster_Coordinator#0.prepared" {
   style=dashed;
   label="prepared";
   node [shape=record, style=filled, fillcolor=white];
   "Coordinator#0.prepared" [label="{  }"];
   }
   "Coordinator#0.state" [label="state = init" shape=ellipse];
   }
   "coordinator" [label="coordinator = role Coordinator#0" shape=ellipse];
   "coordinator" -> "Coordinator#0_placeholder" [lhead="cluster_Coordinator#0"];
   subgraph "cluster_null.participants" {
   style=dashed;
   label="participants";
   "participants" [shape=plaintext, label=<<table border="0" cellborder="1" cellspacing="0" cellpadding="6"><tr>
<td port="before" sides="b"></td></tr>
<tr><td port="0">role Participant#0</td></tr>
<tr><td port="1">role Participant#1</td></tr>
<tr><td port="after" sides="t"></td>
</tr></table>>];
}
"participants":0 -> "Participant#0_placeholder" [lhead="cluster_Participant#0"];
"participants":1 -> "Participant#1_placeholder" [lhead="cluster_Participant#1"];
}
   {{% /graphviz %}}
5. On the left, you will see various buttons for the actions. Click on the `Coordinator#0.Write` button. 
   it should start the sequence diagram. Continue to click on the buttons to see the sequence diagram.
   If you always choose the success path, you will see eventually both the participants and the coordinator 
   reach the `committed` state.
   {{< mermaid class="text-center" >}}
sequenceDiagram
	note left of 'Coordinator#0': Write
	'Coordinator#0' ->> 'Participant#0': Prepare()
	'Participant#0' -->> 'Coordinator#0': ("prepared")
	'Coordinator#0' ->> 'Participant#1': Prepare()
	'Participant#1' -->> 'Coordinator#0': ("prepared")
	'Coordinator#0' ->> 'Participant#0': Commit()
	'Participant#0' -->> 'Coordinator#0': .
	'Coordinator#0' ->> 'Participant#1': Commit()
	'Participant#1' -->> 'Coordinator#0': .
   {{< /mermaid >}}

   {{% graphviz %}}
digraph G {
compound=true;
subgraph "cluster_Participant#0" {
style=dashed;
label="Participant#0";
"Participant#0_placeholder" [label="" shape=point width=0 height=0 style=invis];
"Participant#0.state" [label="state = committed" shape=ellipse];
}
subgraph "cluster_Participant#1" {
style=dashed;
label="Participant#1";
"Participant#1_placeholder" [label="" shape=point width=0 height=0 style=invis];
"Participant#1.state" [label="state = committed" shape=ellipse];
}
subgraph "cluster_Coordinator#0" {
style=dashed;
label="Coordinator#0";
"Coordinator#0_placeholder" [label="" shape=point width=0 height=0 style=invis];
subgraph "cluster_Coordinator#0.prepared" {
style=dashed;
label="prepared";
"Coordinator#0.prepared" [shape=plaintext, label=<<table border="0" cellborder="1" cellspacing="0" cellpadding="6"><tr>
<td port="before" sides="r"></td>
<td port="0">0</td>
<td port="1">1</td>
<td port="after" sides="l"></td>
</tr></table>>];
}

"Coordinator#0.state" [label="state = committed" shape=ellipse];
}
"coordinator" [label="coordinator = role Coordinator#0" shape=ellipse];
"coordinator" -> "Coordinator#0_placeholder" [lhead="cluster_Coordinator#0"];
subgraph "cluster_null.participants" {
style=dashed;
label="participants";
"participants" [shape=plaintext, label=<<table border="0" cellborder="1" cellspacing="0" cellpadding="6"><tr>
<td port="before" sides="b"></td></tr>
<tr><td port="0">role Participant#0</td></tr>
<tr><td port="1">role Participant#1</td></tr>
<tr><td port="after" sides="t"></td>
</tr></table>>];
}
"participants":0 -> "Participant#0_placeholder" [lhead="cluster_Participant#0"];
"participants":1 -> "Participant#1_placeholder" [lhead="cluster_Participant#1"];
}
   {{% /graphviz %}}

6. Play around with the explorer to see what happens when a participant aborted.
   {{< mermaid class="text-center" >}}
   sequenceDiagram
   note left of 'Coordinator#0': Write
   'Coordinator#0' ->> 'Participant#0': Prepare()
   'Participant#0' -->> 'Coordinator#0': ("prepared")
   'Coordinator#0' ->> 'Participant#1': Prepare()
   'Participant#1' -->> 'Coordinator#0': ("aborted")
   'Coordinator#0' ->> 'Participant#0': Abort()
   'Participant#0' -->> 'Coordinator#0': .
   'Coordinator#0' ->> 'Participant#1': Abort()
   'Participant#1' -->> 'Coordinator#0': .
   {{< /mermaid >}}

   {{% graphviz %}}
   digraph G {
   compound=true;
   subgraph "cluster_Participant#0" {
   style=dashed;
   label="Participant#0";
   "Participant#0_placeholder" [label="" shape=point width=0 height=0 style=invis];
   "Participant#0.state" [label="state = aborted" shape=ellipse];
   }
   subgraph "cluster_Participant#1" {
   style=dashed;
   label="Participant#1";
   "Participant#1_placeholder" [label="" shape=point width=0 height=0 style=invis];
   "Participant#1.state" [label="state = aborted" shape=ellipse];
   }
   subgraph "cluster_Coordinator#0" {
   style=dashed;
   label="Coordinator#0";
   "Coordinator#0_placeholder" [label="" shape=point width=0 height=0 style=invis];
   subgraph "cluster_Coordinator#0.prepared" {
   style=dashed;
   label="prepared";
   "Coordinator#0.prepared" [shape=plaintext, label=<<table border="0" cellborder="1" cellspacing="0" cellpadding="6"><tr>
<td port="before" sides="r"></td>
<td port="0">0</td>
<td port="after" sides="l"></td>
</tr></table>>];
}

"Coordinator#0.state" [label="state = aborted" shape=ellipse];
}
"coordinator" [label="coordinator = role Coordinator#0" shape=ellipse];
"coordinator" -> "Coordinator#0_placeholder" [lhead="cluster_Coordinator#0"];
subgraph "cluster_null.participants" {
style=dashed;
label="participants";
"participants" [shape=plaintext, label=<<table border="0" cellborder="1" cellspacing="0" cellpadding="6"><tr>
<td port="before" sides="b"></td></tr>
<tr><td port="0">role Participant#0</td></tr>
<tr><td port="1">role Participant#1</td></tr>
<tr><td port="after" sides="t"></td>
</tr></table>>];
}
"participants":0 -> "Participant#0_placeholder" [lhead="cluster_Participant#0"];
"participants":1 -> "Participant#1_placeholder" [lhead="cluster_Participant#1"];
}
   {{% /graphviz %}}
7. You can explorer most possible sequences and states.


## Example 2: Insertion Sort
Let's try another visualization - the Insertion Sort algorithm. FizzBee is a formal
verification language, so verifying Insertion Sort is not the best use case. But this introduces
the visualization capabilities.

If you look at the insertion_sort method, the code is actually a working python code
(with only the method definition syntax being different)

### Checkpoint

Checkpoint is similar to breakpoint in debugger, but this is not running the code during exploration
instead it executes the model and checkpoints the state at various points.

There are default checkpoints at the start of each action, any non-determinism
or when there are any yields.

You can set explicit checkpoints using `` `checkpoint` ``.

### FizzBee spec

{{% fizzbee %}}
---
deadlock_detection: false
options:
       max_actions: 1
---

atomic action InsertionSort:
    insertion_sort(arr)

atomic func insertion_sort(arr):
	if len(arr) <= 1:
		return # If the array has 0 or 1 element, it is already sorted, so return

	for i in range(1, len(arr)): # Iterate over the array starting from the second element
        cur = i
        ins = i-1
        
		key = arr[i] # Store the current element as the key to be inserted in the right position
		
        j = i-1  
        `checkpoint`  
    	while j >= 0 and key < arr[j]: # Move elements greater than key one position ahead
                ins = j
    			arr[j+1] = arr[j] # Shift elements to the right
                
                `checkpoint`  
    			j -= 1
                
		arr[j+1] = key # Insert the key in the correct position

action Init:
    # Sorting the array [12, 11, 13, 5, 6] using insertionSort
    # arr = [5, 3, 2, 4, 1]
    arr = [12, 11, 13, 5, 6]
    # arr = ["a12", "a11", "a13", "a5", "a6", "a1"]
    cur = len(arr)
    ins = -1
    key = arr[0]


{{% /fizzbee %}}

1. Run the above code in the playground with `Enable Whiteboard` checked.
2. Click on the `Explorer` link in the console
3. Play around by clicking the buttons. It will only show the states, there are no
   sequence diagrams for this example. (Sequence diagrams are only generated when there are roles)
4. While the states are shown, with `cur` and `ins` variable, it would be nicer
   to show them as pointers to the position in the array. This information is not
   available in the spec so far. So this should be added as an additional config.
   {{% graphviz %}}
   digraph G {
   compound=true;
   subgraph "cluster_null.arr" {
   style=dashed;
   label="arr";
   "arr" [shape=plaintext, label=<<table border="0" cellborder="1" cellspacing="0" cellpadding="6"><tr>
<td port="before" sides="r"></td>
<td port="0">12</td>
<td port="1">11</td>
<td port="2">13</td>
<td port="3">5</td>
<td port="4">6</td>
<td port="after" sides="l"></td>
</tr></table>>];
}

"cur" [label="cur = 1" shape=ellipse];
"ins" [label="ins = 0" shape=ellipse];
"key" [label="key = 11" shape=ellipse];
}
   {{% /graphviz %}}

5. On the left-bottom, you will see the `Config` text area. Insert the following code.
   ```yaml
   variables:
     cur:
       index_of: arr
     ins:
       index_of: arr
   ```
   {{% graphviz %}}
   digraph G {
   compound=true;
   subgraph "cluster_null.arr" {
   style=dashed;
   label="arr";
   "arr" [shape=plaintext, label=<<table border="0" cellborder="1" cellspacing="0" cellpadding="6"><tr>
<td port="before" sides="r"></td>
<td port="0">12</td>
<td port="1">11</td>
<td port="2">13</td>
<td port="3">5</td>
<td port="4">6</td>
<td port="after" sides="l"></td>
</tr></table>>];
}

"cur" [label="cur = 1" shape=ellipse];
"ins" [label="ins = 0" shape=ellipse];
"key" [label="key = 11" shape=ellipse];
"cur" -> "arr":1;
"ins" -> "arr":0;
}
   {{% /graphviz %}}

6. Click on buttons to see the states change as the algorithm progresses.

# Basic Usage

FizzBee is not a usual visualization tool, it is a design specification system.
You can model your design in an python-like language and use that to validate the design
to check for issues like concurrency, consistency, fault tolerance, then model performance
like error ratio, tail latency distribution and more.

As a design specification, FizzBee generates various visualizations to help you understand
the system behavior that can be shard with your team. This makes it easier to explain the design
for your team to review, saving significant amount of time.

For more details on the language, refer to the [FizzBee Language Reference](/tutorials/getting-started/).

In the document, we will do a quick overview of the language necessary to generate the visualizations
and skip the model checking parts.

## Python datatypes
FizzBee uses a variant of Python syntax, and for the most part relies on Starlark for evaluating expressions.
So all the standard Python datatypes like `int`, `float`, `str`, `list`, `dict` etc are supported.

{{% fizzbee %}}
---
deadlock_detection: false
---

action Init:
    elements = [4, 2, 1, 5, 3]
    cursor = 3
    matrix = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
    obj = {"store_id": 1001, "city": "San Francisco", "sqft": 12000.5}
    ordered = [ ("store_id", 1001), ("city", "San Francisco"), ("sqft", 12000.5)]
    obj_array = [{"name": "Alice", "color": "blue", "score": 10}, {"name": "Bob", "color": "green", "score": 9.5, "lang": ["English", "Spanish"]}]

{{% /fizzbee %}}

{{% hint %}}
The top section is the frontmatter, where you can set various model checking options.

In this example, our spec just initializes the variables, and there are no action after that.
So effectively, this implies the system cannot progress after the Init, so it is considered a deadlock
For this example, we are just suppressing this error. 
{{% /hint %}}

Run this example with the whiteboard enabled, then click on the `Explorer` link in the console.

You should see something like,
{{% graphviz %}}
digraph G {
compound=true;
target="_blank";
"cursor" [label="cursor = 3" shape=ellipse];
subgraph "cluster_null.elements" {
style=dashed;
label="elements";
"elements" [shape=plaintext, label=<<table border="0" cellborder="1" cellspacing="0" cellpadding="6"><tr>
<td port="before" sides="r"></td>
<td port="0">4</td>
<td port="1">2</td>
<td port="2">1</td>
<td port="3">5</td>
<td port="4">3</td>
<td port="after" sides="l"></td>
</tr></table>>];
}

subgraph "cluster_null.matrix" {
style=dashed;
label="matrix";
"matrix" [shape=plaintext, label=<<table border="0" cellborder="1" cellspacing="0" cellpadding="6"><tr>
<td colspan="100" port="before" sides="b" cellpadding="0"></td></tr>
<tr><td port="0">1</td>
<td port="0">2</td>
<td port="0">3</td></tr>
<tr><td port="1">4</td>
<td port="1">5</td>
<td port="1">6</td></tr>
<tr><td port="2">7</td>
<td port="2">8</td>
<td port="2">9</td></tr>
<tr><td colspan="100" port="after"  sides="t" cellpadding="0"></td>
</tr></table>>];
}

subgraph "cluster_null.obj" {
style=dashed;
label="obj";
"obj" [shape=plaintext, label=<
<table border="0" cellborder="1" cellspacing="0" cellpadding="4">
  <tr>
    <td port="keycity">city</td>
    <td port="valuecity" >'San Francisco'</td>
  </tr>
  <tr>
    <td port="keysqft">sqft</td>
    <td port="valuesqft" >12000.5</td>
  </tr>
  <tr>
    <td port="keystore_id">store_id</td>
    <td port="valuestore_id" >1001</td>
  </tr>
</table>
>];
}
subgraph "cluster_null.obj_array" {
style=dashed;
label="obj_array";
"obj_array" [shape=plaintext, label=<<table border="0" cellborder="1" cellspacing="0" cellpadding="6"><tr>
<td><b>name</b></td>
<td><b>color</b></td>
<td><b>score</b></td>
<td><b>lang</b></td></tr>
<tr><td colspan="100" port="before" sides="b" cellpadding="0"></td></tr>
<tr><td port="0">Alice</td>
<td port="0">blue</td>
<td port="0">10</td>
<td port="0"></td></tr>
<tr><td port="1">Bob</td>
<td port="1">green</td>
<td port="1">9.5</td>
<td port="1">['English', 'Spanish']</td></tr>
<tr><td colspan="100" port="after"  sides="t" cellpadding="0"></td>
</tr></table>>];
}

subgraph "cluster_null.ordered" {
style=dashed;
label="ordered";
"ordered" [shape=plaintext, label=<<table border="0" cellborder="1" cellspacing="0" cellpadding="6"><tr>
<td colspan="100" port="before" sides="b" cellpadding="0"></td></tr>
<tr><td port="0">store_id</td>
<td port="0">1001</td></tr>
<tr><td port="1">city</td>
<td port="1">San Francisco</td></tr>
<tr><td port="2">sqft</td>
<td port="2">12000.5</td></tr>
<tr><td colspan="100" port="after"  sides="t" cellpadding="0"></td>
</tr></table>>];
}

}
{{% /graphviz %}}

## Simple actions
Actions are the basic building blocks of the system. They can either represent steps triggered
by the user or the components that are external to the system being modelled.

{{% fizzbee %}}
action Init:
    elements = []

action Produce:
    require len(elements) < 4
    x = any range(4)
    elements.append(x)

action Consume:
    require len(elements) > 0
    elements.pop(0)

{{% /fizzbee %}}

Open the playground, and try the whiteboard. This time you will see, the `elements` list
that is initially empty. On the left, click on the `Produce` button,
then pick an element to add to the list.  
you will see the `elements` getting updated. Once an element is added, you would see
two actions `Produce` and `Consume` available (as shown in the image below). Click on `Consume` to remove the element.

{{% rawhtml %}}
<div class="buttons">
    <button id="undo">Undo</button>
    <div id="link-buttons"><button style="margin: 5px 10px 5px 0px;">Produce</button><button style="margin: 5px 10px 5px 0px;">Consume</button></div>
  </div>
{{% /rawhtml %}}
{{% graphviz %}}
digraph G {
compound=true;
target="_blank";
subgraph "cluster_null.elements" {
style=dashed;
label="elements";
"elements" [shape=plaintext, label=<<table border="0" cellborder="1" cellspacing="0" cellpadding="6"><tr>
<td port="before" sides="r"></td>
<td port="0">2</td>
<td port="1">1</td>
<td port="2">3</td>
<td port="after" sides="l"></td>
</tr></table>>];
}

}
{{% /graphviz %}}

Try Produce multiple times to fill to capacity, then you will see Produce action is not enabled anymore.
This should explain how `require` and `any` keywords work 

## Array index
We saw how to display the datastructure. Many times, we would want to see
how the data access. Since the index information is not preserved, we need to
add a bit of extra configuration.

{{% fizzbee %}}

action Init:
    elements = [1, 2, 3, 4, 5]
    cursor = -1
    value = None

atomic action MoveCursor: 
    if cursor > len(elements):
        cursor = -1
        value = None
    elif cursor < len(elements) - 1:
        cursor += 1
        value = elements[cursor]
    else:
        cursor += 1
        value = None
        
{{% /fizzbee %}}

I will show the block diagram like this.
{{% graphviz %}}
digraph G {
compound=true;
target="_blank";
"cursor" [label="cursor = -1" shape=ellipse];
subgraph "cluster_null.elements" {
style=dashed;
label="elements";
"elements" [shape=plaintext, label=<<table border="0" cellborder="1" cellspacing="0" cellpadding="6"><tr>
<td port="before" sides="r"></td>
<td port="0">1</td>
<td port="1">2</td>
<td port="2">3</td>
<td port="3">4</td>
<td port="4">5</td>
<td port="after" sides="l"></td>
</tr></table>>];
}

"value" [label="value = null" shape=ellipse];
}
{{% /graphviz %}}

Now, to specify the cursor variable points to the index of the elements array,

On the left bottom text area, set
```yaml
variables:
  cursor:
    index_of: elements
```
Now, click the MoveCursor buttons. You will see a diagram like this.

{{% graphviz %}}
digraph G {
compound=true;
target="_blank";
"cursor" [label="cursor = 2" shape=ellipse];
subgraph "cluster_null.elements" {
style=dashed;
label="elements";
"elements" [shape=plaintext, label=<<table border="0" cellborder="1" cellspacing="0" cellpadding="6"><tr>
<td port="before" sides="r"></td>
<td port="0">1</td>
<td port="1">2</td>
<td port="2">3</td>
<td port="3">4</td>
<td port="4">5</td>
<td port="after" sides="l"></td>
</tr></table>>];
}

"value" [label="value = 3" shape=ellipse];
"elements":2 -> "cursor" [dir=back] ;
}
{{% /graphviz %}}

## Checkpoints
In the above example, we saw how each action is a step in the system. Let us try slightly
more complex example where we have a loop.
This is a simple example of summing the elements in the array.
{{% fizzbee %}}

action Init:
    elements = [1, 2, 3, 4, 5]
    cursor = -1
    sum = 0

atomic action Sum:
    require sum == 0
    for i in range(0, len(elements)):
        cursor = i
        sum += elements[i]

atomic action Restart:
    require sum != 0
    cursor = -1
    sum = 0

{{% /fizzbee %}}

One action `Sum` sums the results, and the next action `Restart` resets the sum and cursor.

If you run this, you will see the sum being calculated. But you will not see the intermediate steps.

The states graph will show,
{{% graphviz %}}
digraph G {
"0x14000121c20" [label="yield
Actions: 0, Forks: 0
State: {\"cursor\":\"-1\",\"elements\":\"[1, 2, 3, 4, 5]\",\"sum\":\"0\"}
", color="black" penwidth="2" ];
"0x14000121c20" -> "0x14000121f20" [label="Sum", color="black" penwidth="1" ];
"0x14000121f20" [label="yield
Actions: 1, Forks: 1
State: {\"cursor\":\"4\",\"elements\":\"[1, 2, 3, 4, 5]\",\"sum\":\"15\"}
", color="black" penwidth="2" ];
"0x14000121f20" -> "0x14000121c20" [label="Restart", color="black" penwidth="1" ];
}
{{% /graphviz %}}

To see the intermediate steps, we can add a checkpoint in the loop.
{{% highlight udiff %}}
*** 7,12 ****
--- 7,13 ----
  atomic action Sum:
      require sum == 0
      for i in range(0, len(elements)):
+         `checkpoint` 
          cursor = i
          sum += elements[i]
{{% /highlight %}}

Run and open the states graph, you will see a lot more intermediate steps.

{{% graphviz %}}
digraph G {
  "0x14000095c80" [label="yield
Actions: 0, Forks: 0
State: {\"cursor\":\"-1\",\"elements\":\"[1, 2, 3, 4, 5]\",\"sum\":\"0\"}
", color="black" penwidth="2" ];
  "0x14000095c80" -> "0x140001aa000" [label="Sum", color="black" penwidth="1" ];
  "0x140001aa000" [label="Sum
Actions: 1, Forks: 1
State: {\"cursor\":\"-1\",\"elements\":\"[1, 2, 3, 4, 5]\",\"sum\":\"0\"}
Threads: 0/1
", color="black" penwidth="1" ];
  "0x140001aa000" -> "0x140001aa600" [label="checkpoint[Sum.checkpoint]", color="black" penwidth="1" ];
  "0x140001aa600" [label="checkpoint
Actions: 1, Forks: 2
State: {\"cursor\":\"0\",\"elements\":\"[1, 2, 3, 4, 5]\",\"sum\":\"1\"}
Threads: 0/1
", color="black" penwidth="1" ];
  "0x140001aa600" -> "0x140001aad20" [label="checkpoint[Sum.checkpoint]", color="black" penwidth="1" ];
  "0x140001aad20" [label="checkpoint
Actions: 1, Forks: 3
State: {\"cursor\":\"1\",\"elements\":\"[1, 2, 3, 4, 5]\",\"sum\":\"3\"}
Threads: 0/1
", color="black" penwidth="1" ];
  "0x140001aad20" -> "0x140001ab200" [label="checkpoint[Sum.checkpoint]", color="black" penwidth="1" ];
  "0x140001ab200" [label="checkpoint
Actions: 1, Forks: 4
State: {\"cursor\":\"2\",\"elements\":\"[1, 2, 3, 4, 5]\",\"sum\":\"6\"}
Threads: 0/1
", color="black" penwidth="1" ];
  "0x140001ab200" -> "0x140001ab6e0" [label="checkpoint[Sum.checkpoint]", color="black" penwidth="1" ];
  "0x140001ab6e0" [label="checkpoint
Actions: 1, Forks: 5
State: {\"cursor\":\"3\",\"elements\":\"[1, 2, 3, 4, 5]\",\"sum\":\"10\"}
Threads: 0/1
", color="black" penwidth="1" ];
  "0x140001ab6e0" -> "0x140001abbc0" [label="checkpoint[Sum.checkpoint]", color="black" penwidth="1" ];
  "0x140001abbc0" [label="yield
Actions: 1, Forks: 6
State: {\"cursor\":\"4\",\"elements\":\"[1, 2, 3, 4, 5]\",\"sum\":\"15\"}
", color="black" penwidth="2" ];
  "0x140001abbc0" -> "0x14000095c80" [label="Restart", color="black" penwidth="1" ];
}
{{% /graphviz %}}

Then, open the explorer. Similar to previous example, set the cursor.

```yaml
variables:
  cursor:
    index_of: elements
```
Now, click the Sum button and play.
{{% graphviz %}}
digraph G {
compound=true;
target="_blank";
"cursor" [label="cursor = -1" shape=ellipse];
subgraph "cluster_null.elements" {
style=dashed;
label="elements";
"elements" [shape=plaintext, label=<<table border="0" cellborder="1" cellspacing="0" cellpadding="6"><tr>
<td port="before" sides="r"></td>
<td port="0">1</td>
<td port="1">2</td>
<td port="2">3</td>
<td port="3">4</td>
<td port="4">5</td>
<td port="after" sides="l"></td>
</tr></table>>];
}

"sum" [label="sum = 0" shape=ellipse];
"elements":before -> "cursor" [dir=back] ;
}
{{% /graphviz %}}

## Roles (Required for Sequence Diagrams)
To role more about roles, see [Roles](/tutorials/roles)

Let us take a simple message passing example.

{{% fizzbee %}}
role Sender:
    action Process:
        receiver.Greet("Alice")
        pass

role Receiver:
    func Greet(name):
        return "Hello " + name

action Init:
    sender = Sender()
    receiver = Receiver()

{{% /fizzbee %}}

Once you run with the whiteboard enabled, open the explorer, and click `Process` button, you will see the sequence diagram. 

{{< mermaid class="text-center" >}}
sequenceDiagram
	note left of 'Sender#0': Process
	'Sender#0' ->> 'Receiver#0': Greet(name: "Alice")
	'Receiver#0' -->> 'Sender#0': ("Hello Alice")
{{< /mermaid >}}

As a trivial example, there is only one action and none of these have any states.
Since there are no states, the system does not explore what happens if receiver is not available or if the message is lost,
or the receiver processed it, but the response was lost and so on.

Example: State updates with message passing

{{% fizzbee %}}
---
deadlock_detection: false
---
role Caller:
  action Init:
    self.state = 'init'

  action Send:
    require self.state == 'init'

    self.state = 'calling'
    res = s.Process()
    self.state = 'done'

role Server:
  action Init:
    self.state = 'init'

  func Process():
    self.state = 'done'

action Init:
  r = Caller()
  s = Server()

{{% /fizzbee %}}

When you run it, and open the explorer, you will see the states of the caller and server.
Obviously, 
1. Both the caller and server are in the `init` state.
2. When you click on the `Send` button, the caller changes to `calling`, and server changes to `init` state.
3. At the point, wo possible things can happen.
   i. Happy case: Continue by clicking `thread-0`. The server changes to `done` state. You'll also see a sequence diagram.
   ii. Error case: Error case: Click on `crash`. This path implies, either the caller crashed before sending or server crashed before the server processed the request. So the caller will continue to think it is in calling state.
4. You can similarly try crash after the server processed the request, and see the server in `done` state and caller in `calling` state.
5. Finally, you can try crash after the caller received the response, and see the caller in `done` state and server in `done` state.

An example state where the caller is in `calling` state and server is in `done` state is shown below.


{{< mermaid class="text-center" >}}
sequenceDiagram
	note left of 'Caller#0': Send
	'Caller#0' ->> 'Server#0': Process()
	'Server#0' -->> 'Caller#0': .
	'Caller#0'->>'Caller#0': crash
{{< /mermaid >}}

{{% graphviz %}}
digraph G {
compound=true;
target="_blank";
subgraph "cluster_Caller#0" {
style=dashed;
label="Caller#0";
"Caller#0_placeholder" [label="" shape=point width=0 height=0 style=invis];
"Caller#0.state" [label="state = calling" shape=ellipse];
}
subgraph "cluster_Server#0" {
style=dashed;
label="Server#0";
"Server#0_placeholder" [label="" shape=point width=0 height=0 style=invis];
"Server#0.state" [label="state = done" shape=ellipse];
}
"r" [label="r = role Caller#0" shape=ellipse];
"r" -> "Caller#0_placeholder" [lhead="cluster_Caller#0"];
"s" [label="s = role Server#0" shape=ellipse];
"s" -> "Server#0_placeholder" [lhead="cluster_Server#0"];
}
{{% /graphviz %}}

Now, go back to the first example with two-phase commit and try to understand the behavior.

# Conclusion
FizzBee is a powerful tool to model and visualize the system behavior. In addition to checking for 
correctness, it can also be used to generate visualizations that can be shared with the team to explain the design.

The best of all, unlike any other formal verification system, 
FizzBee uses python'ish language making it easy to ramp up on day 1.

In other visualization tools, you will have to manually create the sequences. Most likely, you won't
be able to create the sequences for all the important paths. But with FizzBee, you can explore all possible paths.
Also, by describing your system design in a precise language, it doubles as a system specification language
replacing significant portions of the design document.
