"""PawPal+ logic layer: core classes for owners, pets, tasks, and scheduling.

This is a skeleton generated from diagrams/uml.mmd. Methods are stubs
(no logic yet) — implement them incrementally per the assignment steps.
"""

from dataclasses import dataclass, field
from datetime import date, datetime, timedelta

_PRIORITY_ORDER = {"high": 0, "medium": 1, "low": 2}
_RECURRING_INTERVALS = {"daily": timedelta(days=1), "weekly": timedelta(weeks=1)}


@dataclass
class Task:
    id: int
    description: str
    duration_mins: int
    priority: str
    due_time: datetime
    is_completed: bool = False
    frequency: str = "once"

    def mark_complete(self) -> None:
        """Mark this task as completed."""
        self.is_completed = True

    def next_occurrence(self, new_id: int) -> "Task | None":
        """Return the next instance of this task if it recurs, else None."""
        interval = _RECURRING_INTERVALS.get(self.frequency)
        if interval is None:
            return None
        return Task(
            id=new_id,
            description=self.description,
            duration_mins=self.duration_mins,
            priority=self.priority,
            due_time=self.due_time + interval,
            frequency=self.frequency,
        )


@dataclass
class Pet:
    id: int
    name: str
    species: str
    age: int
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Add a task to this pet's task list."""
        self.tasks.append(task)

    def remove_task(self, task_id: int) -> None:
        """Remove the task with the given id from this pet's task list, if present."""
        self.tasks = [t for t in self.tasks if t.id != task_id]

    def mark_task_complete(self, task_id: int) -> None:
        """Mark a task complete and, if it recurs, append its next occurrence."""
        task = next((t for t in self.tasks if t.id == task_id), None)
        if task is None:
            return

        task.mark_complete()
        next_id = max((t.id for t in self.tasks), default=0) + 1
        next_task = task.next_occurrence(next_id)
        if next_task is not None:
            self.add_task(next_task)


@dataclass
class Owner:
    name: str
    preferences: list[str] = field(default_factory=list)
    pets: list[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to this owner's list of pets."""
        self.pets.append(pet)

    def remove_pet(self, pet_id: int) -> None:
        """Remove the pet with the given id from this owner's list of pets, if present."""
        self.pets = [p for p in self.pets if p.id != pet_id]

    def get_all_tasks(self) -> list[tuple[Pet, Task]]:
        """Return every (pet, task) pair across all of this owner's pets."""
        return [(pet, task) for pet in self.pets for task in pet.tasks]


@dataclass
class DailyPlan:
    date: date
    scheduled_tasks: list[Task] = field(default_factory=list)
    skipped_tasks: list[Task] = field(default_factory=list)
    reasoning: str = ""

    def explain(self) -> str:
        """Return a human-readable explanation of why this plan looks the way it does."""
        if not self.scheduled_tasks and not self.skipped_tasks:
            return "No tasks were due today."
        return self.reasoning


class Scheduler:
    """Retrieves, prioritizes, and fits tasks into an available time budget."""

    def _fit_to_budget(
        self, pairs: list[tuple[Pet, Task]], available_mins: int
    ) -> tuple[list[tuple[Pet, Task]], list[tuple[Pet, Task]]]:
        """Sort pending (pet, task) pairs by priority/due_time and greedily fit them into available_mins."""
        pending = [(pet, t) for pet, t in pairs if not t.is_completed]
        pending.sort(key=lambda pair: (_PRIORITY_ORDER.get(pair[1].priority, len(_PRIORITY_ORDER)), pair[1].due_time))

        scheduled: list[tuple[Pet, Task]] = []
        skipped: list[tuple[Pet, Task]] = []
        remaining_mins = available_mins

        for pet, task in pending:
            if task.duration_mins <= remaining_mins:
                scheduled.append((pet, task))
                remaining_mins -= task.duration_mins
            else:
                skipped.append((pet, task))

        return scheduled, skipped

    def generate_plan(self, pet: Pet, available_mins: int) -> DailyPlan:
        """Build a DailyPlan for a single pet's tasks within the given time budget."""
        pairs = [(pet, t) for t in pet.tasks]
        scheduled, skipped = self._fit_to_budget(pairs, available_mins)

        reasoning_lines = [
            f"Scheduled '{t.description}' (priority: {t.priority}, {t.duration_mins} min)."
            for _, t in scheduled
        ]
        reasoning_lines += [
            f"Skipped '{t.description}' - not enough time remaining ({t.duration_mins} min needed)."
            for _, t in skipped
        ]
        reasoning = "\n".join(reasoning_lines) if reasoning_lines else "No pending tasks for this pet."

        return DailyPlan(
            date=date.today(),
            scheduled_tasks=[t for _, t in scheduled],
            skipped_tasks=[t for _, t in skipped],
            reasoning=reasoning,
        )

    def sort_by_time(self, tasks: list[Task]) -> list[Task]:
        """Return tasks sorted earliest-due-time first."""
        return sorted(tasks, key=lambda t: t.due_time)

    def filter_tasks(
        self,
        pairs: list[tuple[Pet, Task]],
        pet_name: str | None = None,
        is_completed: bool | None = None,
    ) -> list[tuple[Pet, Task]]:
        """Filter (pet, task) pairs by pet name and/or completion status."""
        result = pairs
        if pet_name is not None:
            result = [(p, t) for p, t in result if p.name == pet_name]
        if is_completed is not None:
            result = [(p, t) for p, t in result if t.is_completed == is_completed]
        return result

    def detect_conflicts(self, owner: Owner) -> list[str]:
        """Return a warning message for every group of tasks that share the exact same due_time."""
        pairs = owner.get_all_tasks()
        by_time: dict[datetime, list[tuple[Pet, Task]]] = {}
        for pet, task in pairs:
            by_time.setdefault(task.due_time, []).append((pet, task))

        warnings = []
        for due_time, group in by_time.items():
            if len(group) > 1:
                names = ", ".join(f"'{t.description}' ({p.name})" for p, t in group)
                warnings.append(f"Conflict at {due_time}: {names} are all scheduled at the same time.")
        return warnings

    def generate_plan_for_owner(self, owner: Owner, available_mins: int) -> DailyPlan:
        """Build a single DailyPlan spanning all of an owner's pets within the given time budget."""
        pairs = owner.get_all_tasks()
        scheduled, skipped = self._fit_to_budget(pairs, available_mins)

        reasoning_lines = [
            f"Scheduled '{t.description}' for {pet.name} (priority: {t.priority}, {t.duration_mins} min)."
            for pet, t in scheduled
        ]
        reasoning_lines += [
            f"Skipped '{t.description}' for {pet.name} - not enough time remaining ({t.duration_mins} min needed)."
            for pet, t in skipped
        ]
        reasoning = "\n".join(reasoning_lines) if reasoning_lines else "No pending tasks across any pets."

        return DailyPlan(
            date=date.today(),
            scheduled_tasks=[t for _, t in scheduled],
            skipped_tasks=[t for _, t in skipped],
            reasoning=reasoning,
        )
