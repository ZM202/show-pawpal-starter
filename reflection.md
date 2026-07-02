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

Yes. My AI assistant flagged that `Scheduler` originally accepted `available_mins` in both its constructor and in `generate_plan()`, which was redundant and left it ambiguous whether the time budget was fixed per-Scheduler or per-call. I decided to make `Scheduler` stateless and keep `available_mins` only as a parameter to `generate_plan()`, since the time a pet owner has available can reasonably change from day to day — a fixed value set once in the constructor wouldn't reflect that. I updated both `pawpal_system.py` and `diagrams/uml.mmd` to drop the constructor parameter.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

The scheduler considers two constraints: available time (`available_mins`) and task priority (`high`/`medium`/`low`). Already-completed tasks are filtered out before scheduling since they don't need to be planned again. Tasks are sorted by priority first, then by `due_time` as a tiebreaker when two tasks share the same priority. Priority mattered most because the scenario is about a busy owner who needs the most important care tasks (e.g., feeding, meds) handled first if time is tight — time available is the hard limit that ultimately decides how many of those prioritized tasks actually fit.

**b. Tradeoffs**

The scheduler is greedy: it walks through tasks in priority order and schedules the first ones that fit in the remaining time, skipping any task that doesn't fit — it never looks ahead to see if skipping a task now would let more tasks fit later. For example, given 40 minutes, a high-priority 30-minute task is scheduled first, which then means several 15-20 minute lower-priority tasks are all skipped, even though two of them might have fit together in the leftover 10 minutes if the algorithm optimized for total time used instead of strict priority order. This tradeoff is reasonable for this scenario because respecting priority (e.g., always doing feeding/meds before optional grooming) is more important to a pet owner than maximizing the raw number of tasks completed — a simpler, predictable "priority always wins" rule is easier to trust and explain than an optimizer that might reorder things unexpectedly.

---

## 3. AI Collaboration

**a. How you used AI**

I used my AI coding assistant throughout the design phase of this project, mainly for:

- **Design brainstorming**: identifying the three core user actions (add/edit a task, generate a daily plan, view today's plan with reasoning) from the scenario in README.md before writing any code.
- **Class brainstorming**: working through which objects the system needed (Owner, Pet, Task, Scheduler, DailyPlan), including deciding whether an `Owner` class and a `DailyPlan` class were worth the extra complexity versus a simpler design.
- **Drafting the UML diagram**: turning the brainstormed classes into a Mermaid `classDiagram` (`diagrams/uml.mmd`), including attributes, method signatures, and relationships between classes.
- **Generating the skeleton**: converting the UML into `pawpal_system.py` — dataclasses for `Task`, `Pet`, `Owner`, and `DailyPlan`, plus a plain `Scheduler` class, all with empty/stubbed methods.
- **Reviewing the skeleton for gaps**: asking the assistant to look over `pawpal_system.py` for missing relationships or inconsistencies before writing real logic.

The most helpful prompts were the ones that asked the assistant to review my design and point out inconsistencies or missing pieces, rather than just generate a "final" answer to accept as-is.

**b. Judgment and verification**

When reviewing the generated skeleton, the AI pointed out that `Scheduler` took `available_mins` in both `__init__` and `generate_plan()`, and asked me to decide which one to keep rather than picking for me. I evaluated the tradeoff myself: a constructor-only value would assume a fixed daily time budget, while a method-only value allows it to vary per call. Since a pet owner's available time realistically changes day to day, I chose the stateless (method-parameter) version instead of just accepting whichever option was listed first. I verified the change by checking that it was applied consistently in both `pawpal_system.py` and `diagrams/uml.mmd`.

---

## 4. Testing and Verification

**a. What you tested**

In `test_pawpal_system.py` I wrote 7 tests covering:

- A high-priority task gets scheduled before a low-priority one when there isn't enough time for both.
- A task that's longer than the available time gets skipped rather than scheduled.
- Already-completed tasks are excluded from the plan entirely.
- An empty task list produces an empty plan with a clear "no tasks due" message.
- Basic CRUD behavior: adding/removing a task from a `Pet`, adding/removing a `Pet` from an `Owner`, and marking a `Task` complete.

These were important because the scheduling logic (priority ordering + time-budget fitting) is the core value of the app — if it silently scheduled things in the wrong order or double-counted completed tasks, the whole "trustworthy daily plan" idea would fall apart. The CRUD tests matter less for correctness risk but confirm the basic data operations the UI will depend on actually work.

**b. Confidence**

I'm fairly confident the current logic is correct for the cases I tested — all 7 tests pass. I'm less confident about edge cases I haven't tested yet, such as: two tasks with the exact same priority and due time (is the tiebreak stable/deterministic?), a task with `duration_mins` of exactly 0, or tasks with an unrecognized priority value (e.g., a typo like `"med"` instead of `"medium"`) — right now those just sort last via a fallback, which might not be the desired behavior. If I had more time I'd add tests for those cases and for the recurring-task feature mentioned in the README's "Smarter Scheduling" section, which isn't implemented yet.

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
