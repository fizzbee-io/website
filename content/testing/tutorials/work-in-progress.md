---
title: Upcoming Features
description: These are the features not yet implemented, and some work in progress.
weight: 10000
---
The list of planned items are not in any specific order.

- More languages support. Currently supported languages: Go
  - Java (In progress)
  - Rust
  - JavaScript / TypeScript
  - Python
  - C
  - C++
  - Other languages, please let us know!
- Testing RESTful APIs (from OpenAPI specifications) and GRPC APIs (from Protocol Buffers definitions)
  - At present, we would have to manually write the adapter code to call the RESTful APIs. In the future, we will be able to generate the adapter code from OpenAPI specifications.
- Testing Browser-based applications (with Selenium or Playwright)
- Shrinking failing test cases to minimal reproducing cases
- All transitions coverage by implementing state space exploration algorithms like Chinese Postman Problem
- Project management 
  - Display the progress of the implementation and features not implemented (returning NotImplementedError)
- Shared server mode. At present, the server hosts a single state machine. In the future, it will be possible to host multiple state machines on a single server.
