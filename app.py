from datetime import datetime

import streamlit as st

from pawpal_system import Owner, Pet, Scheduler, Task

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")

with st.expander("Scenario", expanded=False):
    st.markdown(
        """
**PawPal+** is a pet care planning assistant. It helps a pet owner plan care tasks
for their pet(s) based on constraints like time, priority, and preferences.
"""
    )

st.divider()

# Persist the Owner (and id counters) in st.session_state so they survive
# Streamlit's top-to-bottom rerun on every interaction.
if "owner" not in st.session_state:
    st.session_state.owner = Owner(name="Jordan")
if "next_pet_id" not in st.session_state:
    st.session_state.next_pet_id = 1
if "next_task_id" not in st.session_state:
    st.session_state.next_task_id = 1

owner: Owner = st.session_state.owner
scheduler = Scheduler()

st.subheader("Owner")
owner.name = st.text_input("Owner name", value=owner.name)

st.divider()

st.subheader("Add a Pet")
col1, col2, col3 = st.columns(3)
with col1:
    new_pet_name = st.text_input("Pet name", value="Mochi")
with col2:
    new_pet_species = st.selectbox("Species", ["dog", "cat", "other"])
with col3:
    new_pet_age = st.number_input("Age", min_value=0, max_value=30, value=1)

if st.button("Add pet"):
    owner.add_pet(
        Pet(id=st.session_state.next_pet_id, name=new_pet_name, species=new_pet_species, age=int(new_pet_age))
    )
    st.session_state.next_pet_id += 1
    st.success(f"Added {new_pet_name} ({new_pet_species}).")

if not owner.pets:
    st.info("No pets yet. Add one above.")
else:
    st.table([{"Name": p.name, "Species": p.species, "Age": p.age} for p in owner.pets])

st.divider()

st.subheader("Add a Task")
if not owner.pets:
    st.info("Add a pet before adding tasks.")
else:
    pet_names = [p.name for p in owner.pets]
    selected_pet_name = st.selectbox("Which pet is this task for?", pet_names)
    selected_pet = next(p for p in owner.pets if p.name == selected_pet_name)

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        task_title = st.text_input("Task title", value="Morning walk")
    with col2:
        duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
    with col3:
        priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)
    with col4:
        frequency = st.selectbox("Frequency", ["once", "daily", "weekly"])

    if st.button("Add task"):
        selected_pet.add_task(
            Task(
                id=st.session_state.next_task_id,
                description=task_title,
                duration_mins=int(duration),
                priority=priority,
                due_time=datetime.now(),
                frequency=frequency,
            )
        )
        st.session_state.next_task_id += 1
        st.success(f"Added '{task_title}' to {selected_pet.name}.")

st.divider()

# --- Sorting, filtering, completion, and conflict detection ---
st.subheader("Today's Tasks")
all_tasks = owner.get_all_tasks()

if not all_tasks:
    st.info("No tasks yet. Add one above.")
else:
    filter_col1, filter_col2 = st.columns(2)
    with filter_col1:
        pet_filter = st.selectbox("Filter by pet", ["All"] + [p.name for p in owner.pets])
    with filter_col2:
        status_filter = st.selectbox("Filter by status", ["All", "Pending", "Completed"])

    filtered_pairs = scheduler.filter_tasks(
        all_tasks,
        pet_name=None if pet_filter == "All" else pet_filter,
        is_completed=None if status_filter == "All" else status_filter == "Completed",
    )
    filtered_tasks = [t for _, t in filtered_pairs]
    sorted_tasks = scheduler.sort_by_time(filtered_tasks)
    pet_by_task_id = {t.id: p.name for p, t in filtered_pairs}

    st.write("Sorted by time:")
    st.table(
        [
            {
                "Time": t.due_time.strftime("%H:%M"),
                "Pet": pet_by_task_id[t.id],
                "Task": t.description,
                "Priority": t.priority,
                "Frequency": t.frequency,
                "Completed": "✅" if t.is_completed else "—",
            }
            for t in sorted_tasks
        ]
    )

    pending_tasks = [t for t in sorted_tasks if not t.is_completed]
    if pending_tasks:
        complete_task_label = st.selectbox(
            "Mark a task complete",
            [f"{pet_by_task_id[t.id]} - {t.description}" for t in pending_tasks],
        )
        if st.button("Mark complete"):
            index = [f"{pet_by_task_id[t.id]} - {t.description}" for t in pending_tasks].index(complete_task_label)
            task_to_complete = pending_tasks[index]
            pet = next(p for p in owner.pets if p.name == pet_by_task_id[task_to_complete.id])
            task_count_before = len(pet.tasks)
            pet.mark_task_complete(task_to_complete.id)
            if len(pet.tasks) > task_count_before:
                st.success(f"'{task_to_complete.description}' completed — next occurrence scheduled automatically.")
            else:
                st.success(f"'{task_to_complete.description}' marked complete.")

    conflicts = scheduler.detect_conflicts(owner)
    if conflicts:
        for warning in conflicts:
            st.warning(f"⚠️ {warning}")
    else:
        st.success("No scheduling conflicts detected.")

st.divider()

st.subheader("Build Schedule")
available_mins = st.number_input(
    "Available time today (minutes)", min_value=1, max_value=720, value=60
)

if st.button("Generate schedule"):
    if not owner.get_all_tasks():
        st.info("Add at least one task above before generating a schedule.")
    else:
        plan = scheduler.generate_plan_for_owner(owner, available_mins=int(available_mins))

        st.markdown(f"### Today's plan for {owner.name}'s pets")
        if plan.scheduled_tasks:
            st.write("**Scheduled:**")
            st.table(
                [
                    {"Task": t.description, "Minutes": t.duration_mins, "Priority": t.priority}
                    for t in plan.scheduled_tasks
                ]
            )
        if plan.skipped_tasks:
            st.write("**Skipped:**")
            st.table(
                [
                    {"Task": t.description, "Minutes": t.duration_mins, "Priority": t.priority}
                    for t in plan.skipped_tasks
                ]
            )

        st.write("**Why this plan:**")
        st.text(plan.explain())
