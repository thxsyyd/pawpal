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
from datetime import time
from enum import Enum
from typing import List, Tuple


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
        pass


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
        """Append a task to this pet's task list."""
        pass

    def remove_task(self, task_id: int) -> None:
        """Remove a task from this pet by its task_id."""
        pass

    def get_tasks(self) -> List[Task]:
        """Return the pet's task list."""
        pass


# ---------------------------------------------------------------------
# Owner
# ---------------------------------------------------------------------

class Owner:
    """An owner, managing multiple pets."""

    def __init__(self, name: str) -> None:
        self.name: str = name
        self.pets: List[Pet] = []

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to this owner."""
        pass

    def remove_pet(self, pet_name: str) -> None:
        """Remove a pet from this owner by name."""
        pass

    def get_all_tasks(self) -> List[Tuple[Pet, Task]]:
        """Return a list of (pet, task) pairs for every task across all pets."""
        pass


# ---------------------------------------------------------------------
# Scheduler
# ---------------------------------------------------------------------

class Scheduler:
    """Service class that builds daily schedules from an Owner's data."""

    def __init__(self, owner: Owner) -> None:
        self.owner: Owner = owner

    def build_daily_schedule(self) -> List[Tuple[Pet, Task]]:
        """Return today's schedule as (pet, task) pairs sorted by time."""
        pass

    def sort_by_time(
        self,
        pairs: List[Tuple[Pet, Task]],
    ) -> List[Tuple[Pet, Task]]:
        """Sort a list of (pet, task) pairs by task.scheduled_time."""
        pass

    def detect_conflicts(
        self,
        pairs: List[Tuple[Pet, Task]],
    ) -> List[str]:
        """Return warning messages for tasks that overlap in time."""
        pass

    def generate_recurring_tasks(self) -> None:
        """Materialize the next occurrence for any DAILY/WEEKLY task marked complete."""
        pass
