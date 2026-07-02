"""PawPal+ logic layer: core classes for owners, pets, tasks, and scheduling.

This is a skeleton generated from diagrams/uml.mmd. Methods are stubs
(no logic yet) — implement them incrementally per the assignment steps.
"""

from dataclasses import dataclass, field
from datetime import date, datetime

_PRIORITY_ORDER = {"high": 0, "medium": 1, "low": 2}


@dataclass
class Task:
    id: int
    description: str
    duration_mins: int
    priority: str
    due_time: datetime
    is_completed: bool = False

    def mark_complete(self) -> None:
        """Mark this task as completed."""
        self.is_completed = True


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
