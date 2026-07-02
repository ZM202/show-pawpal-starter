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

A second tradeoff is in `Scheduler.detect_conflicts()`: it only flags tasks that share the *exact same* `due_time`, not tasks whose durations overlap (e.g., a 30-minute task starting at 8:00 and another starting at 8:15 would not be flagged, even though they overlap in practice). I chose exact-time matching because it's simple to implement and explain, and it still catches the most obvious case (two tasks the owner explicitly scheduled for the same moment). The tradeoff is reasonable for a first pass because true overlap detection would require treating `due_time` as a real start time with a fixed duration window, which the current data model doesn't fully commit to yet — but it does mean some real overlaps could slip through undetected.

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

**c. AI strategy**

The most effective AI assistant feature for this project was having it flag inconsistencies and ask me to make the call, rather than just generating a "finished" answer — the `Scheduler` constructor/method duplication is the clearest example, but the same pattern showed up again when I decided how `Scheduler.detect_conflicts()` should define a "conflict" (exact time match vs. true overlap). In both cases, the AI proposed the simplest version and explicitly documented it as a tradeoff instead of silently picking one, which let me decide on purpose rather than inherit a hidden assumption.

The concrete example of a suggestion I modified is that same `Scheduler` constructor issue from Section 1b/3b: the AI's skeleton had accepted an ambiguous design (time budget settable in two places) that would have caused confusing bugs later (e.g., a stale `available_mins` set once at construction silently overriding what I passed to `generate_plan()`). I rejected the ambiguity and forced a single source of truth.

Using a fresh conversation for architecturally distinct phases (design/UML, then testing, then UI polish) helped me stay organized because each conversation only had the context relevant to that phase — when I asked for a testing plan, I wasn't dragging along the entire history of scheduling-logic debates, so the AI's answers stayed focused and I could evaluate them against a smaller, clearer set of assumptions.

The biggest takeaway about being the "lead architect" is that the AI is very good at generating a technically valid design quickly, but it defaults to the simplest version of any ambiguous decision unless asked to flag it — my job was to keep questioning those defaults (is a `DailyPlan` class worth it? should the Scheduler be stateless? is exact-time conflict detection good enough?) rather than accepting the first working version. The AI is a fast implementer of decisions; deciding what tradeoffs are acceptable for *this* scenario stayed my responsibility throughout.

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

I'm most satisfied with how closely the final `Scheduler.generate_plan()` logic matches what was actually drafted in the UML — going through Step 1 (core actions) and Step 2 (building blocks) before writing any code meant the class design barely needed to change once I started implementing. The one change that did happen (making `Scheduler` stateless) was a small, well-reasoned tweak rather than a rework.

**b. What you would improve**

If I had another iteration, I'd address the gaps identified in Section 4b: validating `priority` against a fixed set of allowed values instead of accepting any string, deciding explicitly how same-priority/same-due-time ties should break, and implementing the recurring-task feature (`Task.frequency`) that's currently just a placeholder in the "Smarter Scheduling" table. I'd also make the greedy scheduling algorithm smarter — right now a single large high-priority task can crowd out several smaller tasks that would have fit in the same time, which isn't necessarily the best outcome for the owner.

**c. Key takeaway**

Doing the UML design and brainstorming (Steps 1-2) before writing any code made the implementation phase noticeably smoother — most of the "hard thinking" (what classes exist, what they're responsible for, how they relate) was already resolved by the time I wrote `pawpal_system.py`, so implementation was mostly translating a decision I'd already made rather than making new ones under pressure. On the AI collaboration side, the most useful moments weren't when the assistant just generated code, but when it flagged a specific inconsistency (like the duplicate `available_mins` parameter) and asked me to make the judgment call instead of deciding for me.
