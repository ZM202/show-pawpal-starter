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
pytest

# Run with coverage:
pytest --cov
```

Sample test output:

```
collected 16 items

test_pawpal_system.py::test_high_priority_task_scheduled_before_low_priority PASSED [  6%]
test_pawpal_system.py::test_task_skipped_when_it_does_not_fit_in_available_time PASSED [ 12%]
test_pawpal_system.py::test_completed_tasks_are_excluded_from_the_plan PASSED [ 18%]
test_pawpal_system.py::test_empty_task_list_produces_empty_plan PASSED   [ 25%]
test_pawpal_system.py::test_pet_add_and_remove_task PASSED               [ 31%]
test_pawpal_system.py::test_owner_add_and_remove_pet PASSED              [ 37%]
test_pawpal_system.py::test_mark_complete_sets_is_completed PASSED       [ 43%]
test_pawpal_system.py::test_sort_by_time_orders_tasks_earliest_first PASSED [ 50%]
test_pawpal_system.py::test_filter_tasks_by_pet_name PASSED              [ 56%]
test_pawpal_system.py::test_filter_tasks_by_completion_status PASSED     [ 62%]
test_pawpal_system.py::test_mark_task_complete_creates_next_occurrence_for_daily_task PASSED [ 68%]
test_pawpal_system.py::test_mark_task_complete_does_not_recur_for_one_time_task PASSED [ 75%]
test_pawpal_system.py::test_detect_conflicts_flags_tasks_at_the_same_time PASSED [ 81%]
test_pawpal_system.py::test_detect_conflicts_returns_empty_when_no_overlap PASSED [ 87%]
tests/test_pawpal.py::test_mark_complete_changes_task_status PASSED      [ 93%]
tests/test_pawpal.py::test_adding_task_increases_pet_task_count PASSED   [100%]

============================== 16 passed in 0.08s ==============================
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

Describe your app in numbered steps so a reader can follow along without watching a video:

1. Run `streamlit run app.py` and open the app in your browser.
2. Enter an owner name, pet name, and species in the "Quick Demo Inputs" section.
3. Add one or more tasks using the task title, duration, and priority fields, clicking "Add task" for each one.
4. Set "Available time today (minutes)" to however much time you have.
5. Click "Generate schedule" to see which tasks were scheduled, which were skipped, and the reasoning behind each decision.

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or link to a demo video here -->
