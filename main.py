"""Demo script: builds sample data and prints today's schedule to the terminal."""

from datetime import datetime

from pawpal_system import Owner, Pet, Scheduler, Task


def build_demo_owner() -> Owner:
    owner = Owner(name="Jordan")

    luna = Pet(id=1, name="Luna", species="dog", age=4)
    luna.add_task(Task(1, "Morning walk", 30, "high", datetime(2026, 7, 2, 8, 0)))
    luna.add_task(Task(2, "Dinner", 15, "high", datetime(2026, 7, 2, 18, 0)))

    milo = Pet(id=2, name="Milo", species="cat", age=2)
    milo.add_task(Task(3, "Brush fur", 20, "low", datetime(2026, 7, 2, 12, 0)))

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
    plan = Scheduler().generate_plan_for_owner(owner, available_mins=45)
    print_schedule(plan)
