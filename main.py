"""
PawPal+ CLI demo.

A standalone script that exercises the whole domain model (Owner, Pet,
Task, Scheduler) end-to-end from the terminal, without any Streamlit UI.

This is the "CLI-first" verification: if `python main.py` prints a
reasonable schedule with all four scheduling features working (sorting,
filtering, conflict detection, recurring tasks), the backend is solid
and we can safely wire it into the UI.

Run:
    python main.py
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
# Pretty-printing helpers
# ---------------------------------------------------------------------

DIVIDER = "━" * 60


def print_header(title: str) -> None:
    """Print a bold, framed section header."""
    print()
    print(DIVIDER)
    print(f"  {title}")
    print(DIVIDER)


def print_schedule(schedule) -> None:
    """Pretty-print a list of (pet, task) pairs as an aligned table."""
    if not schedule:
        print("  (no pending tasks)")
        return
    for pet, task in schedule:
        time_str = task.scheduled_time.strftime("%H:%M")
        print(
            f"  {time_str}  "
            f"{pet.name:<10}"
            f"{task.description:<25}"
            f"({task.duration_minutes} min) "
            f"[{task.priority.value.upper()}]"
        )


# ---------------------------------------------------------------------
# Demo
# ---------------------------------------------------------------------

def main() -> None:
    # --- 1. Set up owner and pets ---
    owner = Owner(name="Haoxuan")

    biscuit = Pet(name="Biscuit", species="dog")
    mochi = Pet(name="Mochi", species="cat")
    owner.add_pet(biscuit)
    owner.add_pet(mochi)

    # --- 2. Add tasks (intentionally out of order to show sorting) ---
    biscuit.add_task(
        Task(1, "Evening walk", time(18, 0), 30, Priority.MEDIUM, Frequency.DAILY)
    )
    biscuit.add_task(
        Task(2, "Breakfast", time(8, 0), 15, Priority.HIGH, Frequency.DAILY)
    )
    biscuit.add_task(
        Task(3, "Vet appointment", time(8, 10), 30, Priority.HIGH, Frequency.ONE_TIME)
    )
    mochi.add_task(
        Task(4, "Feeding", time(7, 30), 10, Priority.HIGH, Frequency.DAILY)
    )
    mochi.add_task(
        Task(5, "Playtime", time(20, 0), 20, Priority.LOW, Frequency.DAILY)
    )

    # --- 3. Build today's schedule ---
    scheduler = Scheduler(owner)
    schedule = scheduler.build_daily_schedule()

    print_header(f"🐾 PawPal+ — Today's Schedule for {owner.name}")
    print_schedule(schedule)

    # --- 4. Detect conflicts across pets ---
    print_header("⚠️  Conflict Detection")
    warnings = scheduler.detect_conflicts(schedule)
    if warnings:
        for w in warnings:
            print(f"  • {w}")
    else:
        print("  No conflicts detected.")

    # --- 5. Mark some tasks complete ---
    print_header("✅ Marking tasks complete")
    biscuit.get_tasks()[1].mark_complete()  # Breakfast
    mochi.get_tasks()[0].mark_complete()  # Feeding
    print("  Marked complete: Biscuit's Breakfast, Mochi's Feeding")

    print_header("🐾 Updated schedule (completed tasks filtered out)")
    print_schedule(scheduler.build_daily_schedule())

    # --- 6. Generate recurring tasks for tomorrow ---
    print_header("🔁 Generating recurring tasks for next occurrence")
    before = sum(len(p.tasks) for p in owner.pets)
    scheduler.generate_recurring_tasks()
    after = sum(len(p.tasks) for p in owner.pets)
    print(f"  Total tasks: {before} → {after}")
    print("  (Completed DAILY/WEEKLY tasks spawned fresh instances for next time)")

    print_header("🐾 Schedule after recurrence")
    print_schedule(scheduler.build_daily_schedule())

    print()
    print(DIVIDER)
    print("  Demo complete.")
    print(DIVIDER)


if __name__ == "__main__":
    main()
