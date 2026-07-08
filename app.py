"""
PawPal+ Streamlit app.

The UI layer for the pet care scheduling system. All business logic lives
in `pawpal_system.py`; this file just wires user inputs to that model and
displays results.

Run:
    streamlit run app.py
"""

from datetime import time

import streamlit as st

from pawpal_system import (
    Frequency,
    Owner,
    Pet,
    Priority,
    Scheduler,
    Task,
)


# ---------------------------------------------------------------------
# Page config
# ---------------------------------------------------------------------

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")
st.title("🐾 PawPal+")
st.caption("A pet care scheduling assistant.")


# ---------------------------------------------------------------------
# Session state: create one persistent Owner across reruns
# ---------------------------------------------------------------------

if "owner" not in st.session_state:
    st.session_state.owner = Owner(name="Jordan")
if "next_task_id" not in st.session_state:
    st.session_state.next_task_id = 1


owner: Owner = st.session_state.owner


def new_task_id() -> int:
    """Return a fresh task id and advance the counter."""
    task_id = st.session_state.next_task_id
    st.session_state.next_task_id += 1
    return task_id


# ---------------------------------------------------------------------
# Owner section
# ---------------------------------------------------------------------

with st.expander("👤 Owner", expanded=True):
    new_owner_name = st.text_input("Owner name", value=owner.name)
    if new_owner_name != owner.name:
        owner.name = new_owner_name


# ---------------------------------------------------------------------
# Pets section
# ---------------------------------------------------------------------

st.subheader("🐕 Pets")

with st.form("add_pet_form", clear_on_submit=True):
    col1, col2 = st.columns(2)
    with col1:
        pet_name = st.text_input("Pet name", value="")
    with col2:
        species = st.selectbox("Species", ["dog", "cat", "other"])
    submitted = st.form_submit_button("Add pet")
    if submitted:
        if not pet_name.strip():
            st.warning("Please enter a pet name.")
        else:
            try:
                owner.add_pet(Pet(name=pet_name.strip(), species=species))
                st.success(f"Added {pet_name.strip()} ({species}).")
            except ValueError as e:
                st.error(str(e))

if owner.pets:
    st.write("Current pets:")
    for pet in owner.pets:
        col1, col2 = st.columns([4, 1])
        with col1:
            st.write(f"  • **{pet.name}** ({pet.species}) — {len(pet.tasks)} task(s)")
        with col2:
            if st.button("Remove", key=f"remove_pet_{pet.name}"):
                owner.remove_pet(pet.name)
                st.rerun()
else:
    st.info("No pets yet. Add one above.")


# ---------------------------------------------------------------------
# Tasks section
# ---------------------------------------------------------------------

st.subheader("📋 Tasks")

if not owner.pets:
    st.info("Add a pet first before adding tasks.")
else:
    with st.form("add_task_form", clear_on_submit=True):
        pet_name = st.selectbox("Pet", [p.name for p in owner.pets])
        description = st.text_input("Task description", value="Morning walk")

        col1, col2 = st.columns(2)
        with col1:
            hour = st.number_input("Hour (24h)", min_value=0, max_value=23, value=8)
        with col2:
            minute = st.number_input("Minute", min_value=0, max_value=59, value=0)

        col3, col4, col5 = st.columns(3)
        with col3:
            duration = st.number_input("Duration (min)", min_value=1, max_value=240, value=20)
        with col4:
            priority_label = st.selectbox("Priority", ["high", "medium", "low"])
        with col5:
            frequency_label = st.selectbox("Frequency", ["one_time", "daily", "weekly"])

        submitted = st.form_submit_button("Add task")
        if submitted:
            pet = next(p for p in owner.pets if p.name == pet_name)
            try:
                pet.add_task(
                    Task(
                        task_id=new_task_id(),
                        description=description,
                        scheduled_time=time(int(hour), int(minute)),
                        duration_minutes=int(duration),
                        priority=Priority(priority_label),
                        frequency=Frequency(frequency_label),
                    )
                )
                st.success(f"Added '{description}' for {pet_name}.")
            except ValueError as e:
                st.error(str(e))

    # Show current tasks per pet with a "complete" button
    for pet in owner.pets:
        if not pet.tasks:
            continue
        st.write(f"**{pet.name}'s tasks:**")
        for task in pet.get_tasks():
            col1, col2, col3 = st.columns([5, 1, 1])
            with col1:
                status = "✅" if task.is_completed else "⏳"
                st.write(
                    f"  {status}  {task.scheduled_time.strftime('%H:%M')} — "
                    f"{task.description} ({task.duration_minutes} min) "
                    f"[{task.priority.value}, {task.frequency.value}]"
                )
            with col2:
                if not task.is_completed and st.button(
                    "Done", key=f"done_{pet.name}_{task.task_id}"
                ):
                    task.mark_complete()
                    st.rerun()
            with col3:
                if st.button("Delete", key=f"del_{pet.name}_{task.task_id}"):
                    pet.remove_task(task.task_id)
                    st.rerun()


# ---------------------------------------------------------------------
# Schedule section
# ---------------------------------------------------------------------

st.divider()
st.subheader("📅 Today's Schedule")

if st.button("Generate schedule", type="primary"):
    scheduler = Scheduler(owner)
    schedule = scheduler.build_daily_schedule()
    conflicts = scheduler.detect_conflicts(schedule)

    if not schedule:
        st.info("No pending tasks. Add some or mark existing ones as pending.")
    else:
        # Render schedule as a table-like layout
        for pet, task in schedule:
            st.write(
                f"  **{task.scheduled_time.strftime('%H:%M')}** — "
                f"{pet.name}: {task.description} "
                f"({task.duration_minutes} min) [{task.priority.value.upper()}]"
            )

    if conflicts:
        st.warning("⚠️  Scheduling conflicts detected:")
        for c in conflicts:
            st.write(f"  • {c}")
    else:
        st.success("✅ No conflicts detected.")


# ---------------------------------------------------------------------
# Recurring tasks section
# ---------------------------------------------------------------------

st.divider()
st.subheader("🔁 Advance to next day")

st.caption(
    "Completed DAILY or WEEKLY tasks will spawn fresh (uncompleted) copies. "
    "ONE_TIME tasks do not recur."
)

if st.button("Generate next occurrences"):
    scheduler = Scheduler(owner)
    before = sum(len(p.tasks) for p in owner.pets)
    # Assign fresh IDs for the new tasks so they don't clash with existing ones.
    scheduler.generate_recurring_tasks()
    after = sum(len(p.tasks) for p in owner.pets)
    added = after - before
    if added == 0:
        st.info("No recurring tasks to respawn (nothing daily/weekly is completed).")
    else:
        st.success(f"Spawned {added} new recurring task(s).")
    st.rerun()
