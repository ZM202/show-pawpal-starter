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

Terminal output from running `python main.py`, which builds an owner with two pets (Luna, Milo)
and three tasks, then generates a schedule across both pets with 45 available minutes:

```
Today's Schedule (2026-07-02):

Scheduled:
  - Morning walk (30 min) [priority: high]
  - Dinner (15 min) [priority: high]

Skipped:
  - Brush fur (20 min) [priority: low]

Why this plan:
Scheduled 'Morning walk' for Luna (priority: high, 30 min).
Scheduled 'Dinner' for Luna (priority: high, 15 min).
Skipped 'Brush fur' for Milo - not enough time remaining (20 min needed).
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
collected 7 items

test_pawpal_system.py::test_high_priority_task_scheduled_before_low_priority PASSED [ 14%]
test_pawpal_system.py::test_task_skipped_when_it_does_not_fit_in_available_time PASSED [ 28%]
test_pawpal_system.py::test_completed_tasks_are_excluded_from_the_plan PASSED [ 42%]
test_pawpal_system.py::test_empty_task_list_produces_empty_plan PASSED   [ 57%]
test_pawpal_system.py::test_pet_add_and_remove_task PASSED               [ 71%]
test_pawpal_system.py::test_owner_add_and_remove_pet PASSED              [ 85%]
test_pawpal_system.py::test_mark_complete_sets_is_completed PASSED       [100%]

============================== 7 passed in 0.11s ==============================
```

## 📐 Smarter Scheduling

| Feature | Method(s) | Notes |
|---------|-----------|-------|
| Task sorting | `Scheduler.generate_plan()` | Sorts by priority (high → medium → low), then by `due_time` as a tiebreaker |
| Filtering | `Scheduler.generate_plan()` | Greedily fits tasks into `available_mins`; anything that doesn't fit is skipped, not scheduled |
| Conflict handling | *(not implemented)* | Not needed yet since tasks don't have fixed start times, only a duration and a due time |
| Recurring tasks | *(not implemented)* | Stretch feature; `Task.frequency` would need to be added to support "Daily"/"Weekly" regeneration |

## 📸 Demo Walkthrough

Describe your app in numbered steps so a reader can follow along without watching a video:

1. Run `streamlit run app.py` and open the app in your browser.
2. Enter an owner name, pet name, and species in the "Quick Demo Inputs" section.
3. Add one or more tasks using the task title, duration, and priority fields, clicking "Add task" for each one.
4. Set "Available time today (minutes)" to however much time you have.
5. Click "Generate schedule" to see which tasks were scheduled, which were skipped, and the reasoning behind each decision.

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or link to a demo video here -->
