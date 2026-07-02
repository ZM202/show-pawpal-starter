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
        self.is_completed = True


@dataclass
class Pet:
    id: int
    name: str
    species: str
    age: int
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        self.tasks.append(task)

    def remove_task(self, task_id: int) -> None:
        self.tasks = [t for t in self.tasks if t.id != task_id]


@dataclass
class Owner:
    name: str
    preferences: list[str] = field(default_factory=list)
    pets: list[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        self.pets.append(pet)

    def remove_pet(self, pet_id: int) -> None:
        self.pets = [p for p in self.pets if p.id != pet_id]


@dataclass
class DailyPlan:
    date: date
    scheduled_tasks: list[Task] = field(default_factory=list)
    skipped_tasks: list[Task] = field(default_factory=list)
    reasoning: str = ""

    def explain(self) -> str:
        if not self.scheduled_tasks and not self.skipped_tasks:
            return "No tasks were due today."
        return self.reasoning


class Scheduler:
    def generate_plan(self, pet: Pet, available_mins: int) -> DailyPlan:
        pending = [t for t in pet.tasks if not t.is_completed]
        pending.sort(key=lambda t: (_PRIORITY_ORDER.get(t.priority, len(_PRIORITY_ORDER)), t.due_time))

        scheduled: list[Task] = []
        skipped: list[Task] = []
        remaining_mins = available_mins

        for task in pending:
            if task.duration_mins <= remaining_mins:
                scheduled.append(task)
                remaining_mins -= task.duration_mins
            else:
                skipped.append(task)

        reasoning_lines = [
            f"Scheduled '{t.description}' (priority: {t.priority}, {t.duration_mins} min)."
            for t in scheduled
        ]
        reasoning_lines += [
            f"Skipped '{t.description}' — not enough time remaining ({t.duration_mins} min needed)."
            for t in skipped
        ]
        reasoning = "\n".join(reasoning_lines) if reasoning_lines else "No pending tasks for this pet."

        return DailyPlan(
            date=date.today(),
            scheduled_tasks=scheduled,
            skipped_tasks=skipped,
            reasoning=reasoning,
        )
