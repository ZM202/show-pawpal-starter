from datetime import datetime

from pawpal_system import Pet, Task


def test_mark_complete_changes_task_status():
    task = Task(1, "Morning walk", 30, "high", datetime(2026, 7, 2, 8, 0))
    assert task.is_completed is False

    task.mark_complete()

    assert task.is_completed is True


def test_adding_task_increases_pet_task_count():
    pet = Pet(id=1, name="Luna", species="dog", age=4)
    assert len(pet.tasks) == 0

    pet.add_task(Task(1, "Morning walk", 30, "high", datetime(2026, 7, 2, 8, 0)))

    assert len(pet.tasks) == 1
