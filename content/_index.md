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

      <div class="fb-workbench" aria-label="FizzBee model checking preview">
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

  <section class="fb-section fb-section--compact" aria-label="FizzBee workflow">
    <div class="fb-loop" aria-label="FizzBee workflow">
      <div>
        <h3>Model</h3>
        <p>Describe actors, actions, state, faults, and invariants in readable code.</p>
      </div>
      <div>
        <h3>Verify</h3>
        <p>Check every schedule for safety, liveness, deadlocks, and counterexamples.</p>
      </div>
      <div>
        <h3>Visualize</h3>
        <p>Generate sequence diagrams, state views, and traces your team can review.</p>
      </div>
      <div>
        <h3>Test</h3>
        <p>Map the model to real code and exercise every behavior the design allows.</p>
      </div>
    </div>
  </section>

  <section class="fb-section fb-section--split" aria-labelledby="fb-why-title">
    <div class="fb-section__header">
      <h2 id="fb-why-title">Distributed bugs hide in the schedules people do not write down.</h2>
      <p>FizzBee makes the schedules explicit. It checks behavioral correctness, exposes edge cases, and gives teams diagrams they can review together.</p>
      <a class="fb-text-link" href="/design/examples/">Browse examples</a>
    </div>
    <div class="fb-trace" aria-label="Example design trace">
      <div class="fb-trace__row">
        <span>client</span>
        <strong>Checkout</strong>
        <em>request received</em>
      </div>
      <div class="fb-trace__row">
        <span>coordinator</span>
        <strong>PlaceHold</strong>
        <em>2 participants</em>
      </div>
      <div class="fb-trace__row fb-trace__row--warn">
        <span>participant</span>
        <strong>Abort</strong>
        <em>counterexample avoided</em>
      </div>
      <div class="fb-trace__row">
        <span>test</span>
        <strong>Replay</strong>
        <em>implementation verified</em>
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
