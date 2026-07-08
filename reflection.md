# PawPal+ Project Reflection

## 1. System Design

**Core user actions**

PawPal+ is designed to support these three core user actions:

1. **Add pets and their care tasks** (feedings, walks, medications, appointments, etc.), each with a scheduled time, duration, priority, and frequency (one-time / daily / weekly).
2. **Manage tasks over time**: mark tasks as complete after finishing them; edit or delete tasks as the pet's routine changes.
3. **Generate today's schedule**, sorted by time, with warnings for any scheduling conflicts across pets.

**a. Initial design**

The initial UML consists of four core classes plus two supporting Enums:

- **Task** (`@dataclass`) — a single scheduled activity. Holds `task_id`, `description`, `scheduled_time` (using `datetime.time`), `duration_minutes`, `priority` (Enum), `frequency` (Enum), and an `is_completed` flag. Its only behavior is `mark_complete()`.
- **Pet** (`@dataclass`) — a single pet, owning a list of Task instances. Responsible for adding, removing, and returning its own tasks. It knows nothing about other pets or scheduling.
- **Owner** — a person managing multiple pets. Owns a list of Pet instances. Provides `get_all_tasks()` which flattens every pet's tasks into a list of `(Pet, Task)` pairs so callers know which task belongs to which pet.
- **Scheduler** — a service class that consumes an Owner and produces scheduling outputs. All algorithmic logic lives here: sorting by time, filtering out completed tasks, detecting time conflicts, and spawning recurring tasks.
- **Priority** and **Frequency** — Enums (HIGH/MEDIUM/LOW, and ONE_TIME/DAILY/WEEKLY) that keep Task's fields type-safe rather than free-form strings.

The relationships are strictly compositional: Owner *owns* Pets, Pet *owns* Tasks, and Scheduler *uses* Owner. Data lives with the entity classes; algorithms live with the service class.

**b. Design changes**

The most impactful design change happened before I wrote any implementation code. My first draft of Task included a `pet_name` field so that any Task could be displayed with its owner's pet's name without extra lookup. When I asked myself "what happens if the owner renames a pet later?", I realized this duplicated data would silently go out of sync — every existing Task would still carry the old name unless I remembered to update each one.

I removed `pet_name` from Task entirely and adopted the **Single Source of Truth** principle: the pet's name lives only on the Pet object, and any code that needs to display a task alongside its pet retrieves the pet through the `(Pet, Task)` pair returned by `Owner.get_all_tasks()`. This eliminated an entire class of consistency bugs before they could occur, at the cost of one extra field of context traveling with each task in the Scheduler's output — a trade I would make every time.

A second, smaller change was upgrading Task's field types from plain strings to production-grade types. What started as `time = "08:00"`, `priority = "high"`, `frequency = "daily"` became `datetime.time`, `Priority` Enum, and `Frequency` Enum. This let Python correctly compare times when sorting (no more `"23:00" < "9:00"` bug from lexicographic ordering) and made invalid values impossible to construct by accident.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

The scheduler currently considers three constraints:

1. **Scheduled time** — the primary ordering axis. All schedule outputs are ascending by `task.scheduled_time`.
2. **Completion status** — completed tasks are filtered out so the daily schedule shows only what still needs to happen.
3. **Time overlap between tasks** — the scheduler warns the owner when any two tasks' `[start, start + duration)` intervals overlap, even if the tasks belong to different pets (a single human owner cannot walk one dog and take another to the vet at the same time).

I decided completion and time were the most fundamental constraints because they directly determine "what does the owner need to do next?" — the app's core question. Conflict detection came third because a schedule that silently books an owner for two overlapping tasks is worse than useless: it looks legitimate but is actually impossible.

Priority (HIGH/MEDIUM/LOW) is stored on every Task but I chose not to re-order the schedule by it, only display it. The reason: a HIGH-priority task at 6 PM should still appear at 6 PM, not jump to the top of the list. Priority is information for the human, not a re-sorting key.

**b. Tradeoffs**

The recurring-task strategy is deliberately simplistic. When a DAILY or WEEKLY task is marked complete, `generate_recurring_tasks()` spawns a fresh copy with the same `scheduled_time` and duration but a new `task_id`. It does not track calendar dates — the new task is just "next time this happens," not "at 08:00 tomorrow" or "at 08:00 next Monday."

The trade this makes: **date semantics are simplified in exchange for a clear, testable model**. Real calendar recurrence (with time zones, DST edge cases, missed occurrences, backfill on weekends, etc.) is a whole subsystem of its own. In the context of a Module 2 project focused on OOP structure and basic algorithmic thinking, adding that complexity would swamp the scheduling logic we're supposed to demonstrate.

The tradeoff is reasonable because the current model still shows the *shape* of recurrence correctly (DAILY tasks respawn, WEEKLY tasks respawn, ONE_TIME tasks do not), and the extension point — attaching real dates to a "next occurrence" — is a natural follow-up rather than a redesign.

---

## 3. AI Collaboration

**a. How you used AI**

I used Claude throughout the project as a design partner, an explainer, and a code reviewer. The most useful modes were:

- **Design brainstorming.** Before writing any code, I described the scenario to the assistant and asked it to help me identify the four required classes, their responsibilities, and their relationships. Rather than accepting the first suggestion, we iterated: it proposed an initial UML, I flagged where things "felt off," and we revised together.
- **Concept explanation.** When I opted into industrial-grade Python (`@dataclass`, Enums, `datetime.time` instead of strings), I asked the assistant to explain each concept, why production code prefers it, and what tradeoffs I was signing up for. That let me understand *what* my code was doing rather than just copying it.
- **Debugging.** Twice during Phase 2, I introduced small bugs while re-organizing code myself (an accidental extra import, misaligned docstring quotes, wrong indentation on a `@staticmethod` decorator). Each time the assistant traced the bugs to their line-level source and explained *why* Python was rejecting the code — not just the fix.
- **Verification prompts.** After each method was implemented, we ran a targeted test snippet that exercised both happy path and failure path. Bugs surfaced immediately instead of piling up.

The most helpful prompts were open-ended and phrased as *questions* about my own design — "does this feel off?", "what if I need to change X later?" — rather than "write me code that does Y."

**b. Judgment and verification**

The clearest moment I overrode an AI suggestion was on the Task `mark_complete()` method. I had extended it to also record a `completed_at` timestamp, reasoning that "this is a natural thing to want later." The assistant pushed back with the **YAGNI** principle ("You Aren't Gonna Need It"): adding a field before there's a concrete need creates additional test surface, an extra import, and one more thing that can be wrong — with no current caller benefiting. I trimmed `mark_complete()` back to `self.is_completed = True` and moved on. The class stayed simple, and when I eventually implement a real completion log, I'll be adding it on top of a clean foundation instead of an accidental one.

More generally, I verified AI output the same way I verify my own: by running the code and checking behavior against expectations. Every method got a smoke test against a hand-constructed case; every algorithmic feature got a pytest that could fail loudly if the logic drifted. When one of my own hand-edits caused four separate syntax errors at once, tests caught it in the next run instead of hiding until submission.

---

## 4. Testing and Verification

**a. What you tested**

The pytest suite in `tests/test_pawpal.py` covers six behaviors, split across three classes:

1. **Task lifecycle** — `test_mark_complete_changes_status` verifies that a newly-constructed task starts uncompleted and that `mark_complete()` flips the flag.
2. **Pet composition** — `test_add_task_increases_pet_task_count` verifies that adding a task grows the pet's task list by exactly one and preserves the exact object reference.
3. **Scheduler sorting** — `test_sort_by_time_orders_ascending` inserts tasks intentionally out of chronological order and asserts the schedule is returned strictly ascending by `scheduled_time`.
4. **Scheduler conflict detection (positive)** — `test_detect_conflicts_flags_overlapping_tasks` sets up two overlapping tasks and asserts exactly one warning is produced, with both task descriptions mentioned in the message.
5. **Scheduler conflict detection (boundary)** — `test_no_conflict_when_tasks_touch_but_do_not_overlap` sets up two tasks that end/start at exactly the same instant and asserts *no* warning is produced. This is the edge case where a strict-vs-non-strict inequality mistake would flip the correctness of the whole detector.
6. **Scheduler recurrence** — `test_generate_recurring_tasks_respawns_daily_but_not_one_time` completes both a DAILY and a ONE_TIME task and asserts that only one new task is spawned, and that the new task is the daily one and is uncompleted.

These behaviors mattered because they are the *contracts* other parts of the system rely on. The Streamlit UI trusts that `mark_complete()` actually completes; `main.py` trusts that the schedule comes back sorted; a future feature that acts on conflict warnings trusts that the detector's boundary behavior is stable. Testing the contracts, not just the internals, is what lets me change implementation details later without breaking users.

**b. Confidence**

I am confident that the scheduler correctly handles the four algorithmic features it advertises: sorting, filtering, conflict detection, and recurrence. Each has a passing test that exercises both the intended behavior and at least one non-obvious edge case (the touching-but-not-overlapping conflict case being the strongest example).

Edge cases I would test next given more time:

- **Empty inputs** — What does `build_daily_schedule()` return for an owner with no pets, or a pet with no tasks? (It should return an empty list, but I haven't asserted it.)
- **Duplicate task IDs across pets** — Right now `Pet.add_task()` rejects a duplicate within one pet, but the same task_id can exist on different pets. Whether that's correct behavior or a latent bug depends on how we want IDs to scope.
- **All-day tasks** — What happens for a task with a very long duration (say 1440 minutes)? The overlap arithmetic uses `datetime.combine(date.today(), ...)`, which quietly assumes tasks fit within a single day.
- **Recurrence chains** — If I call `generate_recurring_tasks()` twice in a row without completing anything new, does it keep spawning? (It shouldn't, but I only test one call.)

---

## 5. Reflection

**a. What went well**

The clearest win was **separating layers up front**: domain model in `pawpal_system.py`, CLI verification in `main.py`, UI in `app.py`, tests in `tests/`. This paid off constantly: I could rewrite the Streamlit layout three times without touching a single line of scheduling logic; I could run pytest in half a second and know that the backend still worked; I could demo the whole system in a terminal before the UI even existed. The "CLI-first" workflow suggested by the assignment turned out to be one of the most transferable ideas from the project.

I'm also glad I chose the industrial-grade type strategy (`@dataclass`, `Enum`, `datetime.time`) rather than the simpler string-based path. It added a small learning cost early but eliminated an entire category of bugs (bad time comparisons, typo'd priority strings) and made the code look and feel closer to what a real team would ship.

**b. What you would improve**

Two things I would redesign given another iteration:

1. **Real calendar dates on tasks.** Right now every task has a time-of-day but no date. Recurrence therefore has no true "next Monday" — only "next time." Adding a `next_due` date field on Task (and letting `generate_recurring_tasks()` advance it based on Frequency) would make the recurrence system actually useful over multiple days.
2. **Persistence.** Everything lives in Streamlit's `session_state`, so closing the app resets the world. Even a minimal pickle-to-disk save/load on every mutation would make the app feel like a real tool rather than a demo.

**c. Key takeaway**

The biggest lesson was that **the value of AI collaboration comes from the questions I ask, not the code it writes**. When I asked "write me a scheduler," the results felt generic and I couldn't defend the design choices. When I asked "does this feel off?" or "what happens if X changes later?", the conversation moved forward in ways I understood and owned. Design-first, with the AI as a thinking partner rather than a code oracle, produced code I could confidently explain and modify.
