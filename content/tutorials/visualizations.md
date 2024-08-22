---
title: Whiteboard Visualizations
weight: 30

---

FizzBee generates multiple visualizations and diagrams. So far you would have seen,
automatically generated state diagrams. In addition to state diagrams, FizzBee also
generates sequence diagrams and algorithm visualizations.

These are helpful in understanding the algorithm and the system behavior. 


{{% toc %}}

If you are design a system or defining an algorithm, with FizzBee you can model check
and prove your design meets all the requirements. While other tools like TLA+, P etc
do the same, FizzBee uses a more Pythonic syntax making it easier to learn and use.

While writing the spec helps you prove the correctness, to explain and share the design to
your teammates the spec is not sufficient. Traditionally you'll explain the design in a design document
giving both the details of the design and the reasoning behind the design.

Usually, the design explanation will involve a lot of diagrams. 

FizzBee generates these diagrams. Better yet, it gives an interactive explorer.

## Enable whiteboard visualizations
On the fizzbee playground, you can enable the whiteboard visualizations by setting
the `Enable Whiteboard` checkbox. Then click `Run` button. 

Once the model checking is done, you can see a link to the `Explorer` in the `Console`.

Clicking on the `Explorer` link will open the explorer in a new tab.

## Two phase commit example
Before we go over the tutorial, let's see a complete working example.

1. Open the [Two Phase Commit](/examples/two_phase_commit_actors/#complete-code) example
in the play ground
2. enable `Enable Whiteboard` checkbox, and Run. 
3. Once the model checker completes, click on the `Explorer` link in the console.
4. You would see the Init state of the system 
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
   {{% mermaid %}}
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
   {{% /mermaid %}}

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
   {{% mermaid %}}
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
   {{% /mermaid %}}

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


## Insertion Sort example
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
