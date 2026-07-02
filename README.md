# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.

## ✨ Features

- **Multi-pet ownership** — an `Owner` can hold any number of `Pet`s, each with its own task list.
- **Priority-aware scheduling** — tasks are scheduled by priority (high → medium → low) and greedily fit into the time available, with skipped tasks and reasoning shown.
- **Sorting by time** — view all of a pet owner's tasks in chronological order regardless of which pet or when they were added.
- **Filtering** — narrow the task list down by pet name and/or completion status.
- **Daily recurrence** — marking a `"daily"` or `"weekly"` task complete automatically schedules its next occurrence.
- **Conflict warnings** — tasks scheduled at the exact same time (across any pets) are flagged with a warning instead of silently colliding.

## 🖥️ Sample Output

Terminal output from running `python main.py`, which builds an owner with two pets (Luna, Milo),
adds tasks out of chronological order, and exercises sorting, filtering, recurring tasks, and
conflict detection before generating a schedule:

```
=== All tasks sorted by time ===
  08:00 - Morning walk
  08:00 - Feed Milo
  12:00 - Brush fur
  18:00 - Dinner

=== Tasks filtered to Luna only ===
  Dinner (Luna)
  Morning walk (Luna)

=== Conflict check ===
  WARNING: Conflict at 2026-07-02 08:00:00: 'Morning walk' (Luna), 'Feed Milo' (Milo) are all scheduled at the same time.

=== Completing a recurring task ===
  Luna now has 3 tasks (original + auto-generated next occurrence).
  - Dinner due 2026-07-02 18:00:00 (completed: False)
  - Morning walk due 2026-07-02 08:00:00 (completed: True)
  - Morning walk due 2026-07-03 08:00:00 (completed: False)

Today's Schedule (2026-07-02):

Scheduled:
  - Feed Milo (10 min) [priority: high]
  - Dinner (15 min) [priority: high]
  - Brush fur (20 min) [priority: low]

Skipped:
  - Morning walk (30 min) [priority: high]

Why this plan:
Scheduled 'Feed Milo' for Milo (priority: high, 10 min).
Scheduled 'Dinner' for Luna (priority: high, 15 min).
Scheduled 'Brush fur' for Milo (priority: low, 20 min).
Skipped 'Morning walk' for Luna - not enough time remaining (30 min needed).
```

## 🧪 Testing PawPal+

```bash
# Run the full test suite:
python -m pytest

# Run with coverage:
pytest --cov
```

`tests/test_pawpal.py` covers both happy paths and edge cases across the core system:
- Basic CRUD: adding/removing tasks and pets, marking a task complete
- Priority-based scheduling: high-priority tasks scheduled first, tasks that don't fit are skipped, completed tasks excluded, an empty task list produces an empty plan
- **Sorting**: tasks are returned in chronological order (`sort_by_time`), including on an empty list
- **Filtering**: tasks filtered by pet name and by completion status
- **Recurrence**: marking a `"daily"` task complete automatically creates the next day's occurrence; a one-time task does not recur
- **Conflict detection**: two tasks at the exact same time are flagged with a warning; no false positives when times don't overlap; no crash on an owner with no pets

**Confidence Level: ⭐⭐⭐⭐☆ (4/5)** — All 17 tests pass and cover the behaviors I consider most important. I'm not at 5/5 because, per `reflection.md` 4b/2b, conflict detection only checks exact time matches (not overlapping durations), and untested edge cases remain (duplicate priority values, zero-duration tasks, unrecognized priority strings).

Sample test output:

```
collected 17 items

tests/test_pawpal.py::test_mark_complete_changes_task_status PASSED      [  5%]
tests/test_pawpal.py::test_adding_task_increases_pet_task_count PASSED   [ 11%]
tests/test_pawpal.py::test_high_priority_task_scheduled_before_low_priority PASSED [ 17%]
tests/test_pawpal.py::test_task_skipped_when_it_does_not_fit_in_available_time PASSED [ 23%]
tests/test_pawpal.py::test_completed_tasks_are_excluded_from_the_plan PASSED [ 29%]
tests/test_pawpal.py::test_empty_task_list_produces_empty_plan PASSED    [ 35%]
tests/test_pawpal.py::test_pet_add_and_remove_task PASSED                [ 41%]
tests/test_pawpal.py::test_owner_add_and_remove_pet PASSED               [ 47%]
tests/test_pawpal.py::test_sort_by_time_orders_tasks_chronologically PASSED [ 52%]
tests/test_pawpal.py::test_sort_by_time_on_empty_list_returns_empty_list PASSED [ 58%]
tests/test_pawpal.py::test_filter_tasks_by_pet_name PASSED               [ 64%]
tests/test_pawpal.py::test_filter_tasks_by_completion_status PASSED      [ 70%]
tests/test_pawpal.py::test_mark_task_complete_creates_next_occurrence_for_daily_task PASSED [ 76%]
tests/test_pawpal.py::test_mark_task_complete_does_not_recur_for_one_time_task PASSED [ 82%]
tests/test_pawpal.py::test_detect_conflicts_flags_tasks_at_the_same_time PASSED [ 88%]
tests/test_pawpal.py::test_detect_conflicts_returns_empty_when_no_overlap PASSED [ 94%]
tests/test_pawpal.py::test_detect_conflicts_on_owner_with_no_pets_returns_empty PASSED [100%]

============================== 17 passed in 0.47s ==============================
```

## 📐 Smarter Scheduling

| Feature | Method(s) | Notes |
|---------|-----------|-------|
| Task sorting | `Scheduler.sort_by_time()` | Sorts a list of tasks earliest-`due_time`-first |
| Priority-aware scheduling | `Scheduler.generate_plan()`, `Scheduler.generate_plan_for_owner()` | Sorts by priority (high → medium → low), then `due_time` as a tiebreaker, then greedily fits tasks into `available_mins` |
| Filtering | `Scheduler.filter_tasks()` | Filters `(pet, task)` pairs by pet name and/or completion status |
| Conflict detection | `Scheduler.detect_conflicts()` | Groups all of an owner's tasks by exact `due_time`; any group with 2+ tasks produces a warning string rather than raising an error |
| Recurring tasks | `Task.next_occurrence()`, `Pet.mark_task_complete()` | Marking a `"daily"`/`"weekly"` task complete automatically appends its next occurrence (`due_time + timedelta`) to the pet's task list |

## 📸 Demo Walkthrough

### Main UI features and actions

The Streamlit UI (`app.py`) lets a user:
- Set the owner's name.
- Add any number of pets (name, species, age).
- Add tasks to a specific pet, including a frequency (`once`/`daily`/`weekly`).
- View all tasks across every pet, sorted by time, filterable by pet and by completion status.
- Mark a task complete — if it's recurring, the next occurrence is scheduled automatically.
- See conflict warnings if two tasks land on the exact same time.
- Generate a daily schedule across all pets given an available time budget.

### Example workflow

1. Run `streamlit run app.py` and open the app in your browser.
2. Enter the owner's name (e.g., "Jordan").
3. Add a pet (e.g., "Luna", dog, age 4) using the "Add a Pet" form.
4. Add a task for Luna (e.g., "Morning walk", 30 min, high priority, daily) using the "Add a Task" form.
5. Add a second pet ("Milo") and a task for Milo at the same time as Luna's task — the "Today's Tasks" section will show a conflict warning for it.
6. Use the pet/status filters to narrow the task list, and note that it's sorted chronologically.
7. Mark Luna's daily task complete — a new occurrence for the next day appears automatically in the task list.
8. Set "Available time today" and click "Generate schedule" to see which tasks were scheduled vs. skipped, and why.

### Key Scheduler behaviors shown

- **Sorting** (`Scheduler.sort_by_time()`): the "Today's Tasks" table is always shown earliest-time-first.
- **Filtering** (`Scheduler.filter_tasks()`): the pet/status dropdowns narrow which tasks are displayed.
- **Conflict warnings** (`Scheduler.detect_conflicts()`): shown as `st.warning` banners above the schedule builder.
- **Recurring tasks** (`Pet.mark_task_complete()` / `Task.next_occurrence()`): completing a daily/weekly task via the UI immediately adds its next occurrence to the task list.
- **Priority-aware scheduling** (`Scheduler.generate_plan_for_owner()`): the generated schedule respects priority and time budget, with reasoning for every scheduled/skipped task.

### Sample CLI output

Running `python main.py` exercises the same Scheduler logic from the terminal, without the UI:

```
=== All tasks sorted by time ===
  08:00 - Morning walk
  08:00 - Feed Milo
  12:00 - Brush fur
  18:00 - Dinner

=== Tasks filtered to Luna only ===
  Dinner (Luna)
  Morning walk (Luna)

=== Conflict check ===
  WARNING: Conflict at 2026-07-02 08:00:00: 'Morning walk' (Luna), 'Feed Milo' (Milo) are all scheduled at the same time.

=== Completing a recurring task ===
  Luna now has 3 tasks (original + auto-generated next occurrence).
  - Dinner due 2026-07-02 18:00:00 (completed: False)
  - Morning walk due 2026-07-02 08:00:00 (completed: True)
  - Morning walk due 2026-07-03 08:00:00 (completed: False)

Today's Schedule (2026-07-02):

Scheduled:
  - Feed Milo (10 min) [priority: high]
  - Dinner (15 min) [priority: high]
  - Brush fur (20 min) [priority: low]

Skipped:
  - Morning walk (30 min) [priority: high]

Why this plan:
Scheduled 'Feed Milo' for Milo (priority: high, 10 min).
Scheduled 'Dinner' for Luna (priority: high, 15 min).
Scheduled 'Brush fur' for Milo (priority: low, 20 min).
Skipped 'Morning walk' for Luna - not enough time remaining (30 min needed).
```

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or link to a demo video here -->
