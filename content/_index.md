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
        <p class="fb-hero__lead">Describe your design in a small Python-like model. FizzBee explores the state space, verifies the design, and turns the model into a test harness for your code.</p>
        <div class="fb-actions" aria-label="Primary actions">
          <a class="fb-button fb-button--primary" href="/design/tutorials/getting-started/">Start modeling</a>
        </div>
      </div>
      <div class="fb-hero__visual" aria-hidden="true">
        <div class="fb-orbit-visual">
          <div class="fb-orbit-field">
            <span class="fb-orbit-ring fb-orbit-ring--outer"></span>
            <span class="fb-orbit-ring fb-orbit-ring--middle"></span>
            <span class="fb-orbit-ring fb-orbit-ring--inner"></span>
            <svg class="fb-orbit-bee" viewBox="0 0 224 144" xmlns="http://www.w3.org/2000/svg" focusable="false">
              <defs>
                <linearGradient id="fb-bee-body-gold" x1="42" y1="34" x2="156" y2="120" gradientUnits="userSpaceOnUse">
                  <stop offset="0" stop-color="#fff12c"/>
                  <stop offset="0.45" stop-color="#f4c15d"/>
                  <stop offset="1" stop-color="#d79613"/>
                </linearGradient>
                <radialGradient id="fb-bee-head-gold" cx="0" cy="0" r="1" gradientTransform="matrix(34 25 -25 34 172 65)" gradientUnits="userSpaceOnUse">
                  <stop offset="0" stop-color="#c59d28"/>
                  <stop offset="0.6" stop-color="#6f540f"/>
                  <stop offset="1" stop-color="#15120b"/>
                </radialGradient>
                <radialGradient id="fb-bee-eye" cx="0" cy="0" r="1" gradientTransform="matrix(13 17 -11 8 186 61)" gradientUnits="userSpaceOnUse">
                  <stop offset="0" stop-color="#eef3ee"/>
                  <stop offset="0.25" stop-color="#1d2420"/>
                  <stop offset="1" stop-color="#050706"/>
                </radialGradient>
                <linearGradient id="fb-bee-wing" x1="45" y1="8" x2="130" y2="68" gradientUnits="userSpaceOnUse">
                  <stop offset="0" stop-color="#fffdf1" stop-opacity="0.72"/>
                  <stop offset="1" stop-color="#d7cda9" stop-opacity="0.34"/>
                </linearGradient>
                <clipPath id="fb-bee-body-clip">
                  <path d="M24 77C24 48 48 30 86 30C127 30 159 51 166 80C173 111 146 130 95 128C52 126 25 108 24 77Z"/>
                </clipPath>
              </defs>
              <path class="fb-orbit-bee__leg" d="M66 105C54 116 49 126 45 139"/>
              <path class="fb-orbit-bee__leg" d="M90 111C81 122 77 131 76 140"/>
              <path class="fb-orbit-bee__leg" d="M124 109C132 121 139 128 149 133"/>
              <path class="fb-orbit-bee__leg" d="M146 98C156 109 166 114 178 114"/>
              <path class="fb-orbit-bee__leg fb-orbit-bee__leg--far" d="M55 97C42 105 34 111 25 122"/>
              <path class="fb-orbit-bee__leg fb-orbit-bee__leg--far" d="M109 101C112 115 117 124 125 132"/>
              <path class="fb-orbit-bee__stinger" d="M23 78L5 111L35 96Z"/>
              <g clip-path="url(#fb-bee-body-clip)">
                <rect x="14" y="22" width="160" height="116" fill="url(#fb-bee-body-gold)"/>
                <path d="M43 20C31 57 34 94 50 132H70C54 89 54 54 72 20Z" fill="#17180f"/>
                <path d="M87 19C78 54 80 94 96 134H119C103 92 102 54 117 19Z" fill="#17180f"/>
                <path d="M134 30C125 61 127 101 142 130H164C150 96 150 63 164 39Z" fill="#17180f"/>
              </g>
              <path class="fb-orbit-bee__body-outline" d="M24 77C24 48 48 30 86 30C127 30 159 51 166 80C173 111 146 130 95 128C52 126 25 108 24 77Z"/>
              <path class="fb-orbit-bee__wing fb-orbit-bee__wing--rear" d="M76 24C51 2 20 0 12 17C3 36 33 65 83 75C105 79 116 74 115 64C113 50 96 42 76 24Z"/>
              <path class="fb-orbit-bee__wing fb-orbit-bee__wing--front" d="M107 24C80 -2 41 -3 33 17C25 39 62 72 121 80C146 83 156 77 153 65C150 51 130 45 107 24Z"/>
              <path class="fb-orbit-bee__wing-vein" d="M50 24C69 32 91 45 119 72"/>
              <path class="fb-orbit-bee__wing-vein" d="M39 35C59 41 84 51 107 72"/>
              <ellipse class="fb-orbit-bee__head" cx="172" cy="70" rx="34" ry="37"/>
              <ellipse class="fb-orbit-bee__eye" cx="185" cy="62" rx="12" ry="18" transform="rotate(5 185 62)"/>
              <circle class="fb-orbit-bee__eye-shine" cx="181" cy="53" r="4"/>
              <path class="fb-orbit-bee__antenna" d="M173 36C176 17 186 10 200 10"/>
              <path class="fb-orbit-bee__antenna" d="M181 38C188 24 201 20 215 23"/>
            </svg>
            <span class="fb-state-dot fb-state-dot--init"><strong>init</strong></span>
            <span class="fb-state-dot fb-state-dot--vote"><strong>vote</strong></span>
            <span class="fb-state-dot fb-state-dot--hold"><strong>hold</strong></span>
            <span class="fb-state-dot fb-state-dot--commit"><strong>commit</strong></span>
            <span class="fb-state-dot fb-state-dot--abort"><strong>abort</strong></span>
            <span class="fb-state-dot fb-state-dot--crash"><strong>crash</strong></span>
          </div>
        </div>
      </div>
    </div>
  </section>

  <section class="fb-section fb-artifact fb-artifact--model" id="model" aria-labelledby="fb-model-title">
    <div class="fb-artifact__copy">
      <h2 id="fb-model-title">Model</h2>
      <p>Capture the protocol directly: participants vote, the coordinator decides, and the assertion documents the consistency rule.</p>
      <a class="fb-text-link" href="/play">Open in playground</a>
    </div>
    <div class="fb-artifact__media">
      <div class="fb-workbench fb-workbench--inline" aria-label="travel_booking.fizz model">
        <div class="fb-workbench__topbar">
          <strong>travel_booking.fizz</strong>
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
      <p>Use the verified model as a test harness. Go, Java, and Rust adapters expose real roles and actions; FizzBee drives the schedules.</p>
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
    <div class="fb-final__copy">
      <h2 id="fb-final-title">Install FizzBee today</h2>
      <p>Tap Homebrew, install the CLI, and add AI agent skills.</p>
    </div>
    <pre class="fb-final__commands" aria-label="FizzBee installation commands"><code>brew tap fizzbee-io/fizzbee
brew install fizzbee
fizz install-skills</code></pre>
  </section>
</div>
{{< /rawhtml >}}
