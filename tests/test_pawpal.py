"""
Automated tests for the PawPal+ domain model.

Covers:
  1. Task.mark_complete() flips the is_completed flag.
  2. Pet.add_task() increases the pet's task count.
  3. Scheduler.sort_by_time() orders tasks by scheduled_time ascending.
  4. Scheduler.detect_conflicts() flags overlapping tasks.
  5. Scheduler.detect_conflicts() does NOT flag tasks that only touch at the boundary.
  6. Scheduler.generate_recurring_tasks() respawns DAILY tasks but not ONE_TIME tasks.

Run from the pawpal/ project root:
    python -m pytest
"""

from datetime import time

from pawpal_system import (
    Frequency,
    Owner,
    Pet,
    Priority,
    Scheduler,
    Task,
)


# ---------------------------------------------------------------------
# Test 1: Task.mark_complete()
# ---------------------------------------------------------------------

def test_mark_complete_changes_status():
    """A newly-created task starts as incomplete; mark_complete() flips the flag."""
    task = Task(
        task_id=1,
        description="Breakfast",
        scheduled_time=time(8, 0),
        duration_minutes=15,
        priority=Priority.HIGH,
        frequency=Frequency.DAILY,
    )

    assert task.is_completed is False, "Task should start uncompleted"

    task.mark_complete()

    assert task.is_completed is True, "mark_complete() should set is_completed to True"


# ---------------------------------------------------------------------
# Test 2: Pet.add_task() increases task count
# ---------------------------------------------------------------------

def test_add_task_increases_pet_task_count():
    """Adding a task to a pet's list increases the count by one."""
    pet = Pet(name="Biscuit", species="dog")
    assert len(pet.tasks) == 0, "New pet should have zero tasks"

    task = Task(
        task_id=1,
        description="Walk",
        scheduled_time=time(9, 0),
        duration_minutes=30,
        priority=Priority.MEDIUM,
        frequency=Frequency.DAILY,
    )
    pet.add_task(task)

    assert len(pet.tasks) == 1, "After add_task, pet should have one task"
    assert pet.tasks[0] is task, "The added task should be the exact instance we passed in"


# ---------------------------------------------------------------------
# Test 3: Scheduler.sort_by_time() orders ascending
# ---------------------------------------------------------------------

def test_sort_by_time_orders_ascending():
    """Scheduler returns tasks sorted by scheduled_time in ascending order."""
    owner = Owner(name="Owner")
    pet = Pet(name="Pet", species="dog")
    owner.add_pet(pet)

    # Add tasks out of order intentionally
    pet.add_task(Task(1, "Late",  time(20, 0), 15, Priority.LOW, Frequency.DAILY))
    pet.add_task(Task(2, "Early", time(7, 0),  15, Priority.LOW, Frequency.DAILY))
    pet.add_task(Task(3, "Mid",   time(12, 0), 15, Priority.LOW, Frequency.DAILY))

    scheduler = Scheduler(owner)
    schedule = scheduler.build_daily_schedule()

    times = [task.scheduled_time for _, task in schedule]
    assert times == sorted(times), f"Schedule should be sorted; got {times}"


# ---------------------------------------------------------------------
# Test 4: Scheduler.detect_conflicts() flags overlaps
# ---------------------------------------------------------------------

def test_detect_conflicts_flags_overlapping_tasks():
    """Two tasks whose time intervals overlap produce exactly one warning."""
    owner = Owner(name="Owner")
    pet = Pet(name="Pet", species="dog")
    owner.add_pet(pet)

    # Overlapping: 08:00-08:15 and 08:10-08:40
    pet.add_task(Task(1, "A", time(8, 0),  15, Priority.HIGH, Frequency.DAILY))
    pet.add_task(Task(2, "B", time(8, 10), 30, Priority.HIGH, Frequency.DAILY))

    scheduler = Scheduler(owner)
    schedule = scheduler.build_daily_schedule()
    warnings = scheduler.detect_conflicts(schedule)

    assert len(warnings) == 1, f"Expected 1 conflict, got {len(warnings)}"
    assert "'A'" in warnings[0] and "'B'" in warnings[0], (
        "Warning should mention both conflicting tasks by name"
    )


# ---------------------------------------------------------------------
# Test 5: Boundary case — touching tasks are NOT a conflict
# ---------------------------------------------------------------------

def test_no_conflict_when_tasks_touch_but_do_not_overlap():
    """Tasks that end exactly when the next one starts should not be flagged."""
    owner = Owner(name="Owner")
    pet = Pet(name="Pet", species="dog")
    owner.add_pet(pet)

    # Touching: A ends at 08:15, B starts at 08:15
    pet.add_task(Task(1, "A", time(8, 0),  15, Priority.MEDIUM, Frequency.DAILY))
    pet.add_task(Task(2, "B", time(8, 15), 15, Priority.MEDIUM, Frequency.DAILY))

    scheduler = Scheduler(owner)
    warnings = scheduler.detect_conflicts(scheduler.build_daily_schedule())

    assert warnings == [], (
        f"Touching (but not overlapping) tasks should not conflict; got {warnings}"
    )


# ---------------------------------------------------------------------
# Test 6: Scheduler.generate_recurring_tasks()
# ---------------------------------------------------------------------

def test_generate_recurring_tasks_respawns_daily_but_not_one_time():
    """Completed DAILY tasks spawn a fresh copy; ONE_TIME tasks do not."""
    owner = Owner(name="Owner")
    pet = Pet(name="Pet", species="dog")
    owner.add_pet(pet)

    pet.add_task(Task(1, "Daily task",    time(8, 0), 15, Priority.HIGH, Frequency.DAILY))
    pet.add_task(Task(2, "One-time task", time(9, 0), 15, Priority.HIGH, Frequency.ONE_TIME))

    # Mark both as completed
    for task in pet.get_tasks():
        task.mark_complete()

    scheduler = Scheduler(owner)
    scheduler.generate_recurring_tasks()

    # 2 originals + 1 respawned DAILY (ONE_TIME does not respawn) = 3
    assert len(pet.tasks) == 3, f"Expected 3 tasks after respawn, got {len(pet.tasks)}"

    # The respawned task must be uncompleted and match the DAILY one
    new_tasks = [t for t in pet.tasks if not t.is_completed]
    assert len(new_tasks) == 1, "Exactly one uncompleted (respawned) task should exist"
    assert new_tasks[0].description == "Daily task", (
        "Respawned task must be the DAILY one, not the ONE_TIME one"
    )
