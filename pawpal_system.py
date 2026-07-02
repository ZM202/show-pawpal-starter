"""PawPal+ logic layer: core classes for owners, pets, tasks, and scheduling.

This is a skeleton generated from diagrams/uml.mmd. Methods are stubs
(no logic yet) — implement them incrementally per the assignment steps.
"""

from dataclasses import dataclass, field
from datetime import date, datetime


@dataclass
class Task:
    id: int
    description: str
    duration_mins: int
    priority: str
    due_time: datetime
    is_completed: bool = False

    def mark_complete(self) -> None:
        raise NotImplementedError


@dataclass
class Pet:
    id: int
    name: str
    species: str
    age: int
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        raise NotImplementedError

    def remove_task(self, task_id: int) -> None:
        raise NotImplementedError


@dataclass
class Owner:
    name: str
    preferences: list[str] = field(default_factory=list)
    pets: list[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        raise NotImplementedError

    def remove_pet(self, pet_id: int) -> None:
        raise NotImplementedError


@dataclass
class DailyPlan:
    date: date
    scheduled_tasks: list[Task] = field(default_factory=list)
    skipped_tasks: list[Task] = field(default_factory=list)
    reasoning: str = ""

    def explain(self) -> str:
        raise NotImplementedError


class Scheduler:
    def __init__(self, available_mins: int):
        self.available_mins = available_mins

    def generate_plan(self, pet: Pet, available_mins: int) -> DailyPlan:
        raise NotImplementedError
