---
Title: FizzBee – Design Reliable, Scalable Distributed Systems
Description: Designing a distributed system? FizzBee makes it easy to model, visualize, and
  validate your design—catching flaws before you code. The easiest-ever formal methods,
  built for developers.
#geekdocNav: false
geekdocAlign: center
geekdocAnchor: false
geekdocBreadcrumb: false
---


{{< columns >}}

### Analyze & Visualize Your Design

- Specify your system design as code. 
- FizzBee automatically:
  - Generates sequence & block diagrams
  - Checks for behavioral correctness
  - Analyzes performance metrics

<--->

### Generate & Run Tests

- Specify how the design maps to your code.
- FizzBee automatically:
    - Exhaustively tests every behavior
    - Simulates faults and edge cases
    - Validates concurrency and integration

{{< /columns >}}

{{% rawhtml %}}
<style>
        .testimonial-slider { display: flex; overflow-x: auto; gap: 2rem; scroll-snap-type: x mandatory; }
        .testimonial { flex: 0 0 450px; padding: 1.5rem; border-radius: 8px; box-shadow: 0 2px 6px rgba(0,0,0,0.1); scroll-snap-align: start; }

</style>
<section class="testimonials">
    <h2>What Engineers Are Saying</h2>
    <div class="testimonial-slider">
        <div class="testimonial">
            <p>"FizzBee upholds the rigor of TLA+ while making formal verification simpler and more accessible for engineers. By leveraging Python, it reduces the learning curve, with the potential to surpass TLA+ as the go-to tool for engineers."</p>
            <strong>— Jack Vanlightly, Principal Technologist, Confluent</strong>
        </div>
        <div class="testimonial">
            <p>"I discovered FizzBee while designing the manifest for SlateDB, an embedded key-value store. FizzBee’s concepts were easy to grasp in hours, and by the next day, I had a working spec that uncovered a real concurrency bug!"</p>
            <strong>— Vignesh Chandramohan, Engineering Manager, Doordash</strong>
        </div>
        <div class="testimonial">
            <p>"FizzBee’s Python-like syntax made it easy to learn and use, unlike other formal methods languages. I picked it up over a weekend and successfully modeled our streaming ingestion platform to identify correctness bugs. It's intuitive and incredibly effective!"</p>
            <strong>— Franklyn D'souza <br> Staff Software Developer, Shopify</strong>
        </div>
        <div class="testimonial">
            <p>"FizzBee cured my fear of formal methods after struggling with TLA+ years ago. It's surprisingly easy to learn and a refreshing experience—something I never thought I could master. Universities should teach FizzBee!"</p>
            <strong>— Li Yazhou<br> Tech Lead, Cloud Platform, Databend</strong>
        </div>
    </div>
</section>
{{% /rawhtml %}}

## Why Model Your System?

{{< figure src="https://storage.googleapis.com/fizzbee-public/website/homepage/what_fizzbee_does_graph.png" alt="Why Model Your System" caption="Modeling helps you explore edge cases, eliminate ambiguity, catch bugs early, and iterate with confidence. In addition to validating the design, you can verify the implementation" >}}


## Try Fizz

Read the [quick start guide](/design/tutorials/getting-started/) to learn how to write your first FizzBee model
or comb through the [examples](/design/examples/)
or tinker with the [FizzBee online playground](/play)

### An example: Travel Booking Service using Two Phase Commit

{{% fizzbee %}}
---
deadlock_detection: false
---
"""
How does a travel booking service ensure that all components in the itinerary are
booked or nothing is booked? Using Two Phase Commit protocol.

Phase 1: The Coordinator (Booking Service) asks all participants (Airline, Hotel, Car Rental) to place a hold on
the resource.
Phase 2:
    a. If all the participants successfully placed a hold on the resource, 
        the Coordinator (Booking Service) asks all participants to commit the booking.
    b. If any of the participants fail to place a hold, 
        the Coordinator (Booking Service) asks all participants to abort the booking.

The core logic is in the Coordinator.Checkout action 
"""

role Participant:
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
  return True

{{% /fizzbee %}}


