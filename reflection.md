# PawPal+ Project Reflection

## 1. System Design

**Core user actions**

A user of PawPal+ should be able to:

1. Add or edit a pet care task, specifying at least its duration and priority.
2. Generate a daily plan for a pet based on the tasks that are due and the time available.
3. View today's plan along with an explanation of why each task was scheduled, skipped, or ordered the way it was.

**a. Initial design**

My initial UML design has five classes:

- **Owner** — represents the pet owner. Holds their name and preferences, and owns a list of `Pet`s. Responsible for adding/removing pets.
- **Pet** — represents an individual animal. Holds identifying info (name, species, age) and its own list of `Task`s. Responsible for adding/removing tasks for itself.
- **Task** — represents a single care item (e.g., walk, feeding, meds). Holds description, duration, priority, due time, and completion status. Responsible for marking itself complete.
- **Scheduler** — the planning engine. Takes a `Pet` and an available time budget, and is responsible for deciding which tasks fit and producing a `DailyPlan`.
- **DailyPlan** — represents the output of scheduling for a given day. Holds the ordered list of scheduled tasks, any tasks that didn't fit (skipped), and a reasoning string. Responsible for explaining why the plan looks the way it does.

The relationships are straightforward one-to-many chains: an `Owner` has many `Pet`s, a `Pet` has many `Task`s, and the `Scheduler` reads a `Pet`'s tasks to generate a `DailyPlan`, which in turn references the `Task`s it scheduled.  Kept the design intentionally simple, no inheritance or complex patterns, since the core problem (matching tasks to available time) doesn't need it.

**b. Design changes**

- Did your design change during implementation?
- If yes, describe at least one change and why you made it.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
