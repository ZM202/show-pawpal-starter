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


def test_mark_complete_sets_is_completed():
    task = make_task(1, "Morning Walk", 20, "high")
    assert task.is_completed is False

    task.mark_complete()
    assert task.is_completed is True
