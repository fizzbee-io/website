---
Title: FizzBee - Design Reliable Distributed Systems
Description: FizzBee helps engineers model, visualize, validate, and test distributed system designs before implementation.
geekdocNav: false
geekdocAlign: left
geekdocAnchor: false
geekdocBreadcrumb: false
---

{{< rawhtml >}}
<div class="fb-home">
  <section class="fb-hero" aria-labelledby="fb-hero-title">
    <div class="fb-hero__inner">
      <div class="fb-hero__copy">
        <h1 id="fb-hero-title">Design reliable, scalable distributed systems</h1>
        <p class="fb-hero__lead">Write a compact, Python-like model. FizzBee explores the behaviors, draws the diagrams, and turns the same design into tests.</p>
        <div class="fb-actions" aria-label="Primary actions">
          <a class="fb-button fb-button--primary" href="/design/tutorials/getting-started/">Start modeling</a>
        </div>
      </div>
      <div class="fb-hero__visual" aria-hidden="true">
        <div class="fb-state-map">
          <span class="fb-state-edge fb-state-edge--one"></span>
          <span class="fb-state-edge fb-state-edge--two"></span>
          <span class="fb-state-edge fb-state-edge--three"></span>
          <span class="fb-state-edge fb-state-edge--four"></span>
          <div class="fb-state-node fb-state-node--init">
            <span>state 00</span>
            <strong>Init</strong>
            <small>participants ready</small>
          </div>
          <div class="fb-state-node fb-state-node--checkout">
            <span>state 12</span>
            <strong>Checkout</strong>
            <small>coordinator in progress</small>
          </div>
          <div class="fb-state-node fb-state-node--crash">
            <span>state 31</span>
            <strong>Crash</strong>
            <small>deadlock found</small>
          </div>
          <div class="fb-state-node fb-state-node--safe">
            <span>assertion</span>
            <strong>Consistent</strong>
            <small>committed != aborted</small>
          </div>
          <div class="fb-state-trace">
            <span>$ fizz check travel_booking.fizz</span>
            <strong>counterexample: Init -> Checkout -> crash</strong>
          </div>
        </div>
      </div>
    </div>
  </section>

  <section class="fb-section fb-artifact fb-artifact--model" id="model" aria-labelledby="fb-model-title">
    <div class="fb-artifact__copy">
      <h2 id="fb-model-title">Model</h2>
      <p>Capture the protocol directly: participants vote, the coordinator decides, and the assertion documents the consistency rule.</p>
    </div>
    <div class="fb-artifact__media">
      <div class="fb-workbench fb-workbench--inline" aria-label="travel_booking.fizz model">
        <div class="fb-workbench__topbar">
          <strong>travel_booking.fizz</strong>
          <a class="fb-workbench__play" href="/play">Open playground</a>
        </div>
        <div class="fb-workbench__body">
          <pre><code>role Participant:
  action Init:
      self.status = "init"

  func placehold():
      vote = any ["accepted", "aborted"]
      self.status = vote
      return self.status

  func finalize(decision):
      self.status = decision


role Coordinator:
    action Init:
        self.status = "init"

    action Checkout:
        require(self.status == "init")
        self.status = "inprogress"
        for p in participants:
              vote = p.placehold()
              if vote == "aborted":
                  self.finalize("aborted")
                  return

        self.finalize("committed")


    func finalize(decision):
        self.status = decision
        for p in participants:
            p.finalize(decision)


NUM_PARTICIPANTS=2

action Init:
    coordinator = Coordinator()
    participants = []
    for i in range(NUM_PARTICIPANTS):
        participants.append(Participant())

always assertion ParticipantsConsistent:
  for p1 in participants:
    for p2 in participants:
      if p1.status == 'committed' and p2.status == 'aborted':
        return False
  return True</code></pre>
        </div>
      </div>
    </div>
  </section>

  <section class="fb-section fb-artifact fb-artifact--verify" id="verify" aria-labelledby="fb-verify-title">
    <div class="fb-artifact__copy">
      <h2 id="fb-verify-title">Verify</h2>
      <p>Run the model checker and get a concrete result: explored states, generated artifacts, and the failing schedule when the design can deadlock.</p>
      <a class="fb-text-link" href="/design/tutorials/getting-started/">Read the model checking guide</a>
    </div>
    <div class="fb-artifact__media">
      <div class="fb-terminal" aria-label="FizzBee CLI verification output">
        <div class="fb-terminal__topbar">
          <strong>$ fizz --output-dir /tmp/fizzbee-home-run /tmp/travel_booking_home.fizz</strong>
        </div>
        <pre><code>DeprecationWarning: 'VAR = any COLLECTION' is deprecated, use 'VAR = oneof COLLECTION' instead
Model checking /tmp/travel_booking_home.json
configFileName: /tmp/fizz.yaml
fizz.yaml not found. Using default options
StateSpaceOptions: options:{max_actions:100 max_concurrent_actions:2}
Nodes: 32, queued: 0, elapsed: 8.489375ms
Time taken for model checking: 8.509541ms
Writen graph dotfile: /tmp/fizzbee-home-run/graph.dot
Writen communication diagram dotfile: /tmp/fizzbee-home-run/communication.dot
DEADLOCK detected
FAILED: Model checker failed
------
Init
--
state: {"coordinator":"role Coordinator#0","participants":["role Participant#0","role Participant#1"]}
Coordinator#0: fields(status = "init")
Participant#0: fields(status = "init")
Participant#1: fields(status = "init")
------
Coordinator#0.Checkout
--
Coordinator#0: fields(status = "inprogress")
Participant#0: fields(status = "init")
Participant#1: fields(status = "init")
------
crash
--
Coordinator#0: fields(status = "inprogress")
Participant#0: fields(status = "init")
Participant#1: fields(status = "init")
------
Writen graph dotfile: /tmp/fizzbee-home-run/error-graph.dot
Writen error states as html: /tmp/fizzbee-home-run/error-states.html</code></pre>
      </div>
    </div>
  </section>

  <section class="fb-section fb-artifact fb-artifact--visualize" id="visualize" aria-labelledby="fb-visualize-title">
    <div class="fb-artifact__copy">
      <h2 id="fb-visualize-title">Visualize</h2>
      <p>The same run emits graph data for the state explorer. The error graph shows the short path from Init to Checkout to the crash state.</p>
      <a class="fb-text-link" href="/design/tutorials/visualizations/">Explore visualizations</a>
    </div>
    <div class="fb-artifact__media">
      <figure class="fb-graph-frame">
        <img src="/img/fizzbee-travel-booking-state-graph.svg" alt="FizzBee state graph for the travel booking model">
      </figure>
    </div>
  </section>

  <section class="fb-section fb-artifact fb-artifact--test" id="test" aria-labelledby="fb-test-title">
    <div class="fb-artifact__copy">
      <h2 id="fb-test-title">Test</h2>
      <p>Use the verified model as a test harness. The Rust adapter exposes real roles and actions; FizzBee drives the schedules.</p>
      <a class="fb-text-link" href="/testing/tutorials/quick-start/">Read the testing guide</a>
    </div>
    <div class="fb-artifact__media">
      <div class="fb-code-window fb-code-window--rust" aria-label="Rust FizzBee MBT harness example">
        <div class="fb-code-window__topbar">
          <strong>checkout_mbt_test.rs</strong>
        </div>
        <pre><code>use async_trait::async_trait;
use fizzbee_mbt::{
    run_mbt_test,
    traits::{DispatchModel, Model},
    types::{Arg, RoleId},
    value::Value,
    TestOptions,
};

struct BookingHarness {
    service: TravelBookingService,
}

#[async_trait]
impl Model for BookingHarness {
    async fn init(&amp;mut self) -&gt; Result&lt;(), fizzbee_mbt::error::MbtError&gt; {
        self.service.reset().await?;
        Ok(())
    }

    async fn cleanup(&amp;mut self) -&gt; Result&lt;(), fizzbee_mbt::error::MbtError&gt; {
        self.service.close().await?;
        Ok(())
    }
}

#[async_trait]
impl DispatchModel for BookingHarness {
    async fn execute(
        &amp;self,
        role_id: &amp;RoleId,
        function_name: &amp;str,
        args: &amp;[Arg],
    ) -&gt; Result&lt;Value, fizzbee_mbt::error::MbtError&gt; {
        match (role_id.role_name.as_str(), function_name) {
            ("Coordinator", "Checkout") =&gt; self.service.checkout(args).await,
            ("Participant", "placehold") =&gt; self.service.placehold(role_id.index).await,
            _ =&gt; Ok(Value::None),
        }
    }

    fn get_roles(&amp;self) -&gt; Result&lt;Vec&lt;RoleId&gt;, fizzbee_mbt::error::MbtError&gt; {
        Ok(vec![RoleId { role_name: "Coordinator".into(), index: 0 }])
    }
}

#[test]
fn checkout_matches_model() {
    run_mbt_test(
        BookingHarness::new(),
        TestOptions { max_actions: Some(12), max_parallel_runs: Some(32), ..Default::default() },
    ).unwrap();
}</code></pre>
      </div>
    </div>
  </section>

  <section class="fb-section fb-section--quotes" aria-labelledby="fb-quotes-title">
    <div class="fb-section__header">
      <h2 id="fb-quotes-title">Formal methods made easy</h2>
    </div>
    <div class="fb-quotes">
      <figure class="fb-quote">
        <blockquote>FizzBee upholds the rigor of TLA+ while making formal verification simpler and more accessible for engineers. By leveraging Python, it reduces the learning curve, with the potential to surpass TLA+ as the go-to tool for engineers.</blockquote>
        <figcaption>Jack Vanlightly, Principal Technologist, Confluent</figcaption>
      </figure>
      <figure class="fb-quote">
        <blockquote>I discovered FizzBee while designing the manifest for SlateDB, an embedded key-value store. FizzBee's concepts were easy to grasp in hours, and by the next day, I had a working spec that uncovered a real concurrency bug!</blockquote>
        <figcaption>Vignesh Chandramohan, Engineering Manager, DoorDash</figcaption>
      </figure>
      <figure class="fb-quote">
        <blockquote>FizzBee's Python-like syntax made it easy to learn and use, unlike other formal methods languages. I picked it up over a weekend and successfully modeled our streaming ingestion platform to identify correctness bugs. It's intuitive and incredibly effective!</blockquote>
        <figcaption>Franklyn D'souza, Staff Software Developer, Shopify</figcaption>
      </figure>
      <figure class="fb-quote">
        <blockquote>FizzBee cured my fear of formal methods after struggling with TLA+ years ago. It's surprisingly easy to learn and a refreshing experience, something I never thought I could master. Universities should teach FizzBee!</blockquote>
        <figcaption>Li Yazhou, Tech Lead, Cloud Platform, Databend</figcaption>
      </figure>
    </div>
  </section>

  <section class="fb-section fb-final" aria-labelledby="fb-final-title">
    <div>
      <h2 id="fb-final-title">Start with a model small enough to review and strong enough to break assumptions.</h2>
    </div>
    <div class="fb-actions">
      <a class="fb-button fb-button--primary" href="/design/tutorials/getting-started/">Read the quick start</a>
      <a class="fb-button fb-button--secondary" href="/play">Use the playground</a>
    </div>
  </section>
</div>
{{< /rawhtml >}}
