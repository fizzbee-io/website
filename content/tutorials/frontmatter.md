---
title: Config and Front Matter
weight: -18
---

FizzBee has some additional features and configurations, that can be enabled via yaml file.

The configuration can either be set with `fizz.yaml` or with front matter in the markdown file.

In the online playground, it doesn't support `fizz.yaml` file yet, so front matter is the only option.

Front matter is a block of YAML at the beginning of a file that is used to set variables for the page. 
The front matter must be the first thing in the file and must take the form of valid YAML set between triple-dashed lines. 

### Available options
The available options are defined in the protocol buffer file [`statespace_options.proto`](https://github.com/fizzbee-io/fizzbee/blob/main/proto/statespace_options.proto) 

For quick reference here is the content of the file as of the writing. The github link above has the most uptodate options

```protobuf
message StateSpaceOptions {
  Options options = 1;
  // Set options like max_actions for individual action instead.
  map<string, Options> action_options = 2;

  // If true, continue exploring the state space of other paths that did not fail.
  bool continue_on_invariant_failures = 3;

  // If true, continue the failed path as well, ignoring the invariant failure.
  // This is almost equivalent to not having the invariant at all, but it can be useful
  // for debugging
  bool continue_path_on_invariant_failures = 4;

  // Default is 'strict' implies liveness check is done TLA+, the other options are 'probabilistic'
  // The probabilisitic model checker is not integrated into the playground but has to be run
  // separately in commandline.
  string liveness = 5;

  // Enable (default/true) or disable deadlock detection
  // Note: explicitly setting it optional, makes this tristate
  optional bool deadlock_detection = 6;
}

message Options {
  int64 max_actions = 1;
  int64 max_concurrent_actions = 2;
}
```

### Deadlock detection
Try this simple example. When you run this, it will show a deadlock violation because
once x reaches 5, the `Incr` action gets disabled, and no other action is possible.

{{% fizzbee %}}

action Init:
    x = 0

action Incr:
    require x < 5
    x += 1

{{% /fizzbee %}}

Sometimes it is useful to disable deadlock detection. So just add `deadlock_detection: false` to the frontmatter.

{{% fizzbee %}}
---
deadlock_detection: false
---

action Init:
    x = 0

action Incr:
    require x < 5
    x += 1

{{% /fizzbee %}}

Now the system will not show the deadlock error.

### Max Actions
You can set the maximum number of actions to be executed in a path (default=100),
or the maximum number of concurrent actions (default=2).

```yaml
---
options:
  max_actions: 10
  max_concurrent_actions: 1

---

```

### Action specific options

You can set options for individual actions as well.

This will be useful to keep the statespace low or finite while testing all the relevant cases.


```yaml
---
action_options:
  Incr:
    max_actions: 5
    max_concurrent_actions: 1
---
    
```

