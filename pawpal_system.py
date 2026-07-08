"""
PawPal+ core domain model.

This module defines the four main classes for the PawPal+ pet care
management system:

  - Task:      A single scheduled care activity for a pet.
  - Pet:       A pet, holding a list of Task instances.
  - Owner:     An owner, holding a list of Pet instances.
  - Scheduler: A service class that builds daily schedules from an Owner.

Two supporting Enums keep the values on Task type-safe:

  - Priority:  HIGH / MEDIUM / LOW
  - Frequency: ONE_TIME / DAILY / WEEKLY

This file is currently a *skeleton*. All method bodies are `pass`
placeholders — the real logic will be implemented in Phase 2.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Tuple
from datetime import datetime, timedelta, date, time


# ---------------------------------------------------------------------
# Value types (Enums)
# ---------------------------------------------------------------------

class Priority(Enum):
    """Task importance ranking."""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class Frequency(Enum):
    """How often a task recurs."""
    ONE_TIME = "one_time"
    DAILY = "daily"
    WEEKLY = "weekly"


# ---------------------------------------------------------------------
# Task
# ---------------------------------------------------------------------

@dataclass
class Task:
    """A single scheduled care activity for a pet (e.g., breakfast at 08:00)."""

    task_id: int
    description: str
    scheduled_time: time
    duration_minutes: int
    priority: Priority
    frequency: Frequency
    is_completed: bool = False

    def mark_complete(self) -> None:
        """Mark this task as completed."""
        self.is_completed = True


# ---------------------------------------------------------------------
# Pet
# ---------------------------------------------------------------------

@dataclass
class Pet:
    """A pet, owning a list of care tasks."""

    name: str
    species: str
    tasks: List[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Append a task to this pet's task list.

        Raises:
            ValueError: If a task with the same task_id already exists.
        """
        existing_ids = {t.task_id for t in self.tasks}
        if task.task_id in existing_ids:
            raise ValueError(
                f"Task with task_id={task.task_id} already exists for pet '{self.name}'."
            )
        self.tasks.append(task)

    def remove_task(self, task_id: int) -> None:
        """Remove a task from this pet by its task_id.

        Raises:
            ValueError: If no task with the given task_id is found.
        """
        for i, task in enumerate(self.tasks):
            if task.task_id == task_id:
                del self.tasks[i]
                return
        raise ValueError(
            f"No task with task_id={task_id} found for pet '{self.name}'."
        )

    def get_tasks(self) -> List[Task]:
        """Return the pet's task list."""
        return self.tasks.copy()


# ---------------------------------------------------------------------
# Owner
# ---------------------------------------------------------------------

class Owner:
    """An owner, managing multiple pets."""

    def __init__(self, name: str) -> None:
        self.name: str = name
        self.pets: List[Pet] = []

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to this owner.

        Raises:
            ValueError: If a pet with the same name already exists.
        """
        existing_names = {p.name for p in self.pets}
        if pet.name in existing_names:
            raise ValueError(
                f"Pet named '{pet.name}' already exists for owner '{self.name}'."
            )
        self.pets.append(pet)

    def remove_pet(self, pet_name: str) -> None:
        """Remove a pet from this owner by name.

        Raises:
            ValueError: If no pet with the given name is found.
    """
        for i, pet in enumerate(self.pets):
            if pet.name == pet_name:
                del self.pets[i]
                return
        raise ValueError(
            f"No pet named '{pet_name}' found for owner '{self.name}'."
        )

    def get_all_tasks(self) -> List[Tuple[Pet, Task]]:
        """Return a list of (pet, task) pairs for every task across all pets."""
        result: List[Tuple[Pet, Task]] = []
        for pet in self.pets:
            for task in pet.get_tasks():
                result.append((pet, task))
        return result


# ---------------------------------------------------------------------
# Scheduler
# ---------------------------------------------------------------------


class Scheduler:
    """Service class that builds daily schedules from an Owner's data."""

    def __init__(self, owner: Owner) -> None:
        self.owner: Owner = owner

    def build_daily_schedule(self) -> List[Tuple[Pet, Task]]:
        """Return today's schedule as (pet, task) pairs sorted by time.

        Only includes tasks that are not yet completed.
        """
        all_pairs = self.owner.get_all_tasks()
        # Filter out completed tasks (algorithm feature: filtering)
        pending = [
            (pet, task) for pet, task in all_pairs if not task.is_completed
        ]
        # Sort by scheduled time (algorithm feature: sorting)
        return self.sort_by_time(pending)

    def sort_by_time(
        self,
        pairs: List[Tuple[Pet, Task]],
    ) -> List[Tuple[Pet, Task]]:
        """Sort a list of (pet, task) pairs by task.scheduled_time."""
        return sorted(pairs, key=lambda pair: pair[1].scheduled_time)
    
    def detect_conflicts(
        self,
        pairs: List[Tuple[Pet, Task]],
    ) -> List[str]:
        """Return warning messages for tasks that overlap in time.

        Compares every pair of tasks. Two tasks conflict if their
        time intervals [start, start + duration) overlap.
        """
        warnings: List[str] = []
        n = len(pairs)
        for i in range(n):
            pet_a, task_a = pairs[i]
            end_a = self._end_time_of(task_a)
            for j in range(i + 1, n):
                pet_b, task_b = pairs[j]
                end_b = self._end_time_of(task_b)
                # Overlap check
                if task_a.scheduled_time < end_b and task_b.scheduled_time < end_a:
                    warnings.append(
                        f"Conflict: {pet_a.name}'s '{task_a.description}' "
                        f"({task_a.scheduled_time.strftime('%H:%M')}"
                        f"-{end_a.strftime('%H:%M')}) "
                        f"overlaps with {pet_b.name}'s '{task_b.description}' "
                        f"({task_b.scheduled_time.strftime('%H:%M')}"
                        f"-{end_b.strftime('%H:%M')})."
                    )
        return warnings

    def generate_recurring_tasks(self) -> None:
        """For every completed DAILY/WEEKLY task, create a fresh copy for next time."""
        for pet in self.owner.pets:
            # Snapshot current tasks (avoid mutating while iterating)
            current_tasks = list(pet.get_tasks())
            for task in current_tasks:
                if task.is_completed and task.frequency in (Frequency.DAILY, Frequency.WEEKLY):
                    # Generate a new task_id
                    new_id = self._next_task_id(pet)
                    # Create a fresh copy (not completed)
                    new_task = Task(
                        task_id=new_id,
                        description=task.description,
                        scheduled_time=task.scheduled_time,
                        duration_minutes=task.duration_minutes,
                        priority=task.priority,
                        frequency=task.frequency,
                        is_completed=False,
                    )
                    pet.add_task(new_task)
    @staticmethod
    def _end_time_of(task: Task) -> time: 
        """Compute the end time of a task from its start time and duration."""
        start = datetime.combine(date.today(), task.scheduled_time)
        end = start + timedelta(minutes=task.duration_minutes)
        return end.time()
    
    @staticmethod
    def _next_task_id(pet: Pet) -> int:
        """Return an unused task_id for this pet."""
        if not pet.tasks:
            return 1
        return max(t.task_id for t in pet.tasks) + 1
