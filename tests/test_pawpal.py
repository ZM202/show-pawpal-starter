from datetime import datetime

from pawpal_system import Owner, Pet, Task, Scheduler


def make_task(id, description, duration_mins, priority, is_completed=False):
    return Task(
        id=id,
        description=description,
        duration_mins=duration_mins,
        priority=priority,
        due_time=datetime(2026, 1, 1, 9, 0),
        is_completed=is_completed,
    )


def test_mark_complete_changes_task_status():
    task = make_task(1, "Morning walk", 30, "high")
    assert task.is_completed is False

    task.mark_complete()

    assert task.is_completed is True


def test_adding_task_increases_pet_task_count():
    pet = Pet(id=1, name="Luna", species="dog", age=4)
    assert len(pet.tasks) == 0

    pet.add_task(make_task(1, "Morning walk", 30, "high"))

    assert len(pet.tasks) == 1


def test_high_priority_task_scheduled_before_low_priority():
    pet = Pet(id=1, name="Luna", species="Dog", age=4)
    pet.add_task(make_task(1, "Brush Fur", 20, "low"))
    pet.add_task(make_task(2, "Morning Walk", 20, "high"))

    plan = Scheduler().generate_plan(pet, available_mins=20)

    assert [t.description for t in plan.scheduled_tasks] == ["Morning Walk"]
    assert [t.description for t in plan.skipped_tasks] == ["Brush Fur"]


def test_task_skipped_when_it_does_not_fit_in_available_time():
    pet = Pet(id=1, name="Milo", species="Cat", age=2)
    pet.add_task(make_task(1, "Vet Visit", 60, "high"))

    plan = Scheduler().generate_plan(pet, available_mins=30)

    assert plan.scheduled_tasks == []
    assert [t.description for t in plan.skipped_tasks] == ["Vet Visit"]


def test_completed_tasks_are_excluded_from_the_plan():
    pet = Pet(id=1, name="Luna", species="Dog", age=4)
    pet.add_task(make_task(1, "Morning Walk", 20, "high", is_completed=True))

    plan = Scheduler().generate_plan(pet, available_mins=60)

    assert plan.scheduled_tasks == []
    assert plan.skipped_tasks == []


def test_empty_task_list_produces_empty_plan():
    pet = Pet(id=1, name="Luna", species="Dog", age=4)

    plan = Scheduler().generate_plan(pet, available_mins=60)

    assert plan.scheduled_tasks == []
    assert plan.skipped_tasks == []
    assert plan.explain() == "No tasks were due today."


def test_pet_add_and_remove_task():
    pet = Pet(id=1, name="Luna", species="Dog", age=4)
    task = make_task(1, "Morning Walk", 20, "high")

    pet.add_task(task)
    assert pet.tasks == [task]

    pet.remove_task(task.id)
    assert pet.tasks == []


def test_owner_add_and_remove_pet():
    owner = Owner(name="Alex")
    pet = Pet(id=1, name="Luna", species="Dog", age=4)

    owner.add_pet(pet)
    assert owner.pets == [pet]

    owner.remove_pet(pet.id)
    assert owner.pets == []


def test_sort_by_time_orders_tasks_chronologically():
    late = Task(1, "Dinner", 15, "high", datetime(2026, 1, 1, 18, 0))
    early = Task(2, "Morning Walk", 20, "high", datetime(2026, 1, 1, 8, 0))
    middle = Task(3, "Brush Fur", 10, "low", datetime(2026, 1, 1, 12, 0))

    sorted_tasks = Scheduler().sort_by_time([late, middle, early])

    assert [t.description for t in sorted_tasks] == ["Morning Walk", "Brush Fur", "Dinner"]


def test_sort_by_time_on_empty_list_returns_empty_list():
    assert Scheduler().sort_by_time([]) == []


def test_filter_tasks_by_pet_name():
    luna = Pet(id=1, name="Luna", species="Dog", age=4)
    milo = Pet(id=2, name="Milo", species="Cat", age=2)
    luna.add_task(make_task(1, "Walk", 20, "high"))
    milo.add_task(make_task(2, "Brush", 10, "low"))
    owner = Owner(name="Alex")
    owner.add_pet(luna)
    owner.add_pet(milo)

    filtered = Scheduler().filter_tasks(owner.get_all_tasks(), pet_name="Milo")

    assert [t.description for _, t in filtered] == ["Brush"]


def test_filter_tasks_by_completion_status():
    pet = Pet(id=1, name="Luna", species="Dog", age=4)
    pet.add_task(make_task(1, "Walk", 20, "high", is_completed=True))
    pet.add_task(make_task(2, "Feed", 10, "high", is_completed=False))
    owner = Owner(name="Alex")
    owner.add_pet(pet)

    filtered = Scheduler().filter_tasks(owner.get_all_tasks(), is_completed=False)

    assert [t.description for _, t in filtered] == ["Feed"]


def test_mark_task_complete_creates_next_occurrence_for_daily_task():
    pet = Pet(id=1, name="Luna", species="Dog", age=4)
    task = Task(1, "Morning Walk", 20, "high", datetime(2026, 1, 1, 8, 0), frequency="daily")
    pet.add_task(task)

    pet.mark_task_complete(task.id)

    assert task.is_completed is True
    assert len(pet.tasks) == 2
    next_task = pet.tasks[1]
    assert next_task.description == "Morning Walk"
    assert next_task.due_time == datetime(2026, 1, 2, 8, 0)
    assert next_task.is_completed is False


def test_mark_task_complete_does_not_recur_for_one_time_task():
    pet = Pet(id=1, name="Luna", species="Dog", age=4)
    task = make_task(1, "Vet Visit", 30, "high")
    pet.add_task(task)

    pet.mark_task_complete(task.id)

    assert len(pet.tasks) == 1


def test_detect_conflicts_flags_tasks_at_the_same_time():
    same_time = datetime(2026, 1, 1, 8, 0)
    luna = Pet(id=1, name="Luna", species="Dog", age=4)
    milo = Pet(id=2, name="Milo", species="Cat", age=2)
    luna.add_task(Task(1, "Walk", 20, "high", same_time))
    milo.add_task(Task(2, "Feed", 10, "high", same_time))
    owner = Owner(name="Alex")
    owner.add_pet(luna)
    owner.add_pet(milo)

    warnings = Scheduler().detect_conflicts(owner)

    assert len(warnings) == 1
    assert "Walk" in warnings[0] and "Feed" in warnings[0]


def test_detect_conflicts_returns_empty_when_no_overlap():
    luna = Pet(id=1, name="Luna", species="Dog", age=4)
    luna.add_task(Task(1, "Walk", 20, "high", datetime(2026, 1, 1, 8, 0)))
    luna.add_task(Task(2, "Feed", 10, "high", datetime(2026, 1, 1, 18, 0)))
    owner = Owner(name="Alex")
    owner.add_pet(luna)

    assert Scheduler().detect_conflicts(owner) == []


def test_detect_conflicts_on_owner_with_no_pets_returns_empty():
    owner = Owner(name="Alex")

    assert Scheduler().detect_conflicts(owner) == []
