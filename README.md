# PawPal+ (Module 2 Project)

**PawPal+** is a Streamlit app that helps a pet owner plan care tasks for their pets. It supports multiple pets, tasks with time / duration / priority / frequency, scheduling across pets, conflict detection, and automatic recurrence of daily/weekly tasks.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (feedings, walks, medications, appointments, etc.)
- Consider constraints (time available, priority, one-time vs recurring)
- Produce a daily plan sorted by time and warn about scheduling conflicts

## What this app does

The final app lets a user:

- Register an **Owner** and add multiple **Pets** (with species)
- Add tasks per pet, each with **description, scheduled time, duration, priority, and frequency**
- **Mark tasks complete**, **edit** any field of an existing task, and **delete** tasks
- **Generate today's schedule** across all pets, sorted by time
- **Detect scheduling conflicts** where two tasks overlap
- **Advance to the next day** to spawn fresh instances of completed daily/weekly tasks (one-time tasks do not recur)

## Architecture

The project separates concerns into two layers:

- `pawpal_system.py` — the domain model and scheduling logic (four classes + two enums, no UI code)
- `app.py` — the Streamlit UI, which only wires user inputs to the domain model
- `main.py` — a CLI demo that exercises the full domain model end-to-end without any UI
- `tests/test_pawpal.py` — automated pytest suite covering all four algorithmic features

See `diagrams/uml.mmd` for the class diagram.

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Run the Streamlit app

```bash
streamlit run app.py
```

### Run the CLI demo (backend verification)

```bash
python main.py
```

### Run the test suite

```bash
python -m pytest -v
```

## 🖥️ Sample Output

Running `python main.py` produces the following end-to-end demonstration of all scheduling features:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  🐾 PawPal+ — Today's Schedule for Haoxuan
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  07:30  Mochi     Feeding                  (10 min) [HIGH]
  08:00  Biscuit   Breakfast                (15 min) [HIGH]
  08:10  Biscuit   Vet appointment          (30 min) [HIGH]
  18:00  Biscuit   Evening walk             (30 min) [MEDIUM]
  20:00  Mochi     Playtime                 (20 min) [LOW]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  ⚠️  Conflict Detection
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  • Conflict: Biscuit's 'Breakfast' (08:00-08:15) overlaps with Biscuit's 'Vet appointment' (08:10-08:40).

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  ✅ Marking tasks complete
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Marked complete: Biscuit's Breakfast, Mochi's Feeding

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  🐾 Updated schedule (completed tasks filtered out)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  08:10  Biscuit   Vet appointment          (30 min) [HIGH]
  18:00  Biscuit   Evening walk             (30 min) [MEDIUM]
  20:00  Mochi     Playtime                 (20 min) [LOW]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  🔁 Generating recurring tasks for next occurrence
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Total tasks: 5 → 7
  (Completed DAILY/WEEKLY tasks spawned fresh instances for next time)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  🐾 Schedule after recurrence
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  07:30  Mochi     Feeding                  (10 min) [HIGH]
  08:00  Biscuit   Breakfast                (15 min) [HIGH]
  08:10  Biscuit   Vet appointment          (30 min) [HIGH]
  18:00  Biscuit   Evening walk             (30 min) [MEDIUM]
  20:00  Mochi     Playtime                 (20 min) [LOW]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Demo complete.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

## 🧪 Testing PawPal+

```bash
python -m pytest -v
```

Test output:

```
===================================== test session starts =====================================
platform darwin -- Python 3.13.13, pytest-9.1.1, pluggy-1.6.0
collected 6 items

tests/test_pawpal.py::test_mark_complete_changes_status PASSED                          [ 16%]
tests/test_pawpal.py::test_add_task_increases_pet_task_count PASSED                     [ 33%]
tests/test_pawpal.py::test_sort_by_time_orders_ascending PASSED                         [ 50%]
tests/test_pawpal.py::test_detect_conflicts_flags_overlapping_tasks PASSED              [ 66%]
tests/test_pawpal.py::test_no_conflict_when_tasks_touch_but_do_not_overlap PASSED       [ 83%]
tests/test_pawpal.py::test_generate_recurring_tasks_respawns_daily_but_not_one_time PASSED [100%]

====================================== 6 passed in 0.02s ======================================
```

The suite covers all four algorithmic features implemented in `Scheduler`, plus a boundary-case test for the conflict detector (touching-but-not-overlapping tasks).

## 📐 Smarter Scheduling

| Feature | Method(s) | Notes |
|---------|-----------|-------|
| Task sorting | `Scheduler.sort_by_time()` | Uses Python's built-in `sorted()` with a lambda key on `task.scheduled_time`. Runs in O(n log n) via Timsort. |
| Filtering | `Scheduler.build_daily_schedule()` | List comprehension filters out tasks where `is_completed == True` so the daily schedule only shows what still needs to be done. |
| Conflict handling | `Scheduler.detect_conflicts()` | Pairwise O(n²) comparison over the schedule. Two tasks conflict when `start_a < end_b AND start_b < end_a` — tasks that only touch at the boundary are not flagged. |
| Recurring tasks | `Scheduler.generate_recurring_tasks()` | For each completed DAILY or WEEKLY task, spawns a fresh (uncompleted) copy with a new `task_id`. ONE_TIME tasks are intentionally excluded. |

## 📸 Demo Walkthrough

1. **Launch the app.** Run `streamlit run app.py`. The browser opens to a PawPal+ page with an Owner section, Pets section, Tasks section, and two action buttons at the bottom.
2. **Enter the owner's name** in the top expander (defaults to "Jordan"). It updates live as you type.
3. **Add pets.** In the "🐕 Pets" section, type a pet name (e.g., "Biscuit"), pick a species, and click **Add pet**. Repeat for a second pet (e.g., "Mochi", cat). Each pet appears in a row with its task count and a **Remove** button.
4. **Add tasks per pet.** In the "📋 Tasks" section, pick a pet from the dropdown, enter a description, set the hour/minute/duration, and choose a priority and frequency. Click **Add task**. Repeat several times, on purpose creating one time overlap between two pets (e.g., Biscuit's Breakfast at 08:00 for 15 min, and Mochi's Vet at 08:10 for 30 min).
5. **Edit or complete tasks.** Every task row has **Done** and **Delete** buttons, plus a **✏️ Edit task** expander for changing any field of the task in place.
6. **Generate the schedule.** Click **Generate schedule**. Pending tasks are listed in ascending time order across both pets, and any overlapping time windows produce a warning.
7. **Advance to the next day.** Click **Generate next occurrences**. Any completed DAILY or WEEKLY task spawns a fresh copy for the next occurrence; ONE_TIME tasks are not respawned. Regenerating the schedule now shows the new tasks alongside anything still pending.

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or link to a demo video here -->
