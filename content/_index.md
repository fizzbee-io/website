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
        <div class="fb-brand-kicker">
          <img src="/bee-left-to-right-512x512.png" alt="" />
          <span>FizzBee</span>
        </div>
        <h1 id="fb-hero-title">Design distributed systems you can test before you build.</h1>
        <p class="fb-hero__lead">Write a compact, Python-like model. FizzBee explores the behaviors, draws the diagrams, and turns the same design into tests.</p>
        <div class="fb-actions" aria-label="Primary actions">
          <a class="fb-button fb-button--primary" href="/design/tutorials/getting-started/">Start modeling</a>
          <a class="fb-button fb-button--secondary" href="/play">Open playground</a>
        </div>
      </div>

      <div class="fb-workbench" aria-label="FizzBee model checking preview">
        <div class="fb-workbench__topbar">
          <span></span><span></span><span></span>
          <strong>travel_booking.fizz</strong>
        </div>
        <div class="fb-workbench__body">
          <pre><code>role Coordinator:
  action Checkout:
    for p in participants:
      vote = p.placehold()
      if vote == "aborted":
        self.finalize("aborted")
        return
    self.finalize("committed")

always assertion Consistent:
  return not mixed_decisions()</code></pre>
          <div class="fb-run-result">
            <div>
              <span class="fb-status-dot"></span>
              <strong>Model check passed</strong>
            </div>
            <p>1,248 states explored across failures, retries, and interleavings.</p>
          </div>
        </div>
      </div>
    </div>
  </section>

  <section class="fb-section fb-section--compact" aria-labelledby="fb-loop-title">
    <div class="fb-section__header">
      <p class="fb-eyebrow">One model, multiple payoffs</p>
      <h2 id="fb-loop-title">Turn a design sketch into executable evidence.</h2>
    </div>
    <div class="fb-loop" aria-label="FizzBee workflow">
      <div>
        <span>01</span>
        <h3>Specify</h3>
        <p>Model actors, actions, faults, and invariants in readable code.</p>
      </div>
      <div>
        <span>02</span>
        <h3>Explore</h3>
        <p>Generate sequence diagrams, state views, counterexamples, and performance signals.</p>
      </div>
      <div>
        <span>03</span>
        <h3>Test</h3>
        <p>Map the model to real code and exercise every behavior the design allows.</p>
      </div>
    </div>
  </section>

  <section class="fb-section fb-section--split" aria-labelledby="fb-why-title">
    <div class="fb-section__header">
      <p class="fb-eyebrow">Why model first</p>
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
      <p class="fb-eyebrow">Used by engineers designing real systems</p>
      <h2 id="fb-quotes-title">Formal methods without the ceremony.</h2>
    </div>
    <div class="fb-quotes">
      <figure class="fb-quote">
        <blockquote>FizzBee upholds the rigor of TLA+ while making formal verification simpler and more accessible for engineers.</blockquote>
        <figcaption>Jack Vanlightly, Principal Technologist, Confluent</figcaption>
      </figure>
      <figure class="fb-quote">
        <blockquote>By the next day, I had a working spec that uncovered a real concurrency bug.</blockquote>
        <figcaption>Vignesh Chandramohan, Engineering Manager, DoorDash</figcaption>
      </figure>
      <figure class="fb-quote">
        <blockquote>The Python-like syntax made it easy to learn and use, unlike other formal methods languages.</blockquote>
        <figcaption>Franklyn D'souza, Staff Software Developer, Shopify</figcaption>
      </figure>
      <figure class="fb-quote">
        <blockquote>FizzBee cured my fear of formal methods after struggling with TLA+ years ago.</blockquote>
        <figcaption>Li Yazhou, Tech Lead, Cloud Platform, Databend</figcaption>
      </figure>
    </div>
  </section>

  <section class="fb-section fb-final" aria-labelledby="fb-final-title">
    <div>
      <p class="fb-eyebrow">Try FizzBee</p>
      <h2 id="fb-final-title">Start with a model small enough to review and strong enough to break assumptions.</h2>
    </div>
    <div class="fb-actions">
      <a class="fb-button fb-button--primary" href="/design/tutorials/getting-started/">Read the quick start</a>
      <a class="fb-button fb-button--secondary" href="/play">Use the playground</a>
    </div>
  </section>
</div>
{{< /rawhtml >}}
