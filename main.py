"""Demo script: builds sample data and prints today's schedule to the terminal."""

from datetime import datetime

from pawpal_system import Owner, Pet, Scheduler, Task


def build_demo_owner() -> Owner:
    owner = Owner(name="Jordan")

    luna = Pet(id=1, name="Luna", species="dog", age=4)
    # Tasks added out of chronological order on purpose, to exercise sort_by_time().
    luna.add_task(Task(1, "Dinner", 15, "high", datetime(2026, 7, 2, 18, 0)))
    luna.add_task(Task(2, "Morning walk", 30, "high", datetime(2026, 7, 2, 8, 0), frequency="daily"))

    milo = Pet(id=2, name="Milo", species="cat", age=2)
    milo.add_task(Task(3, "Brush fur", 20, "low", datetime(2026, 7, 2, 12, 0)))
    # Deliberately scheduled at the same time as Luna's walk, to trigger conflict detection.
    milo.add_task(Task(4, "Feed Milo", 10, "high", datetime(2026, 7, 2, 8, 0)))

    owner.add_pet(luna)
    owner.add_pet(milo)
    return owner


def print_schedule(plan) -> None:
    print(f"Today's Schedule ({plan.date}):\n")

    if plan.scheduled_tasks:
        print("Scheduled:")
        for task in plan.scheduled_tasks:
            print(f"  - {task.description} ({task.duration_mins} min) [priority: {task.priority}]")
    else:
        print("Scheduled: (none)")

    if plan.skipped_tasks:
        print("\nSkipped:")
        for task in plan.skipped_tasks:
            print(f"  - {task.description} ({task.duration_mins} min) [priority: {task.priority}]")

    print("\nWhy this plan:")
    print(plan.explain())


if __name__ == "__main__":
    owner = build_demo_owner()
    scheduler = Scheduler()

    print("=== All tasks sorted by time ===")
    all_tasks = [task for _, task in owner.get_all_tasks()]
    for task in scheduler.sort_by_time(all_tasks):
        print(f"  {task.due_time.strftime('%H:%M')} - {task.description}")

    print("\n=== Tasks filtered to Luna only ===")
    for pet, task in scheduler.filter_tasks(owner.get_all_tasks(), pet_name="Luna"):
        print(f"  {task.description} ({pet.name})")

    print("\n=== Conflict check ===")
    conflicts = scheduler.detect_conflicts(owner)
    if conflicts:
        for warning in conflicts:
            print(f"  WARNING: {warning}")
    else:
        print("  No conflicts found.")

    print("\n=== Completing a recurring task ===")
    luna = owner.pets[0]
    luna.mark_task_complete(2)  # "Morning walk" is a daily task
    print(f"  Luna now has {len(luna.tasks)} tasks (original + auto-generated next occurrence).")
    for task in luna.tasks:
        print(f"  - {task.description} due {task.due_time} (completed: {task.is_completed})")

    print()
    plan = scheduler.generate_plan_for_owner(owner, available_mins=45)
    print_schedule(plan)
