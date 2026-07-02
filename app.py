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

# --- Step 2: persist the Owner (and id counters) in st.session_state so they ---
# --- survive Streamlit's top-to-bottom rerun on every interaction. ---
if "owner" not in st.session_state:
    st.session_state.owner = Owner(name="Jordan")
if "next_pet_id" not in st.session_state:
    st.session_state.next_pet_id = 1
if "next_task_id" not in st.session_state:
    st.session_state.next_task_id = 1

owner: Owner = st.session_state.owner

st.subheader("Owner")
owner.name = st.text_input("Owner name", value=owner.name)

st.divider()

# --- Step 3: wire the "Add Pet" form to Owner.add_pet() ---
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

# --- Step 3: wire the "Add Task" form to Pet.add_task() ---
st.subheader("Add a Task")
if not owner.pets:
    st.info("Add a pet before adding tasks.")
else:
    pet_names = [p.name for p in owner.pets]
    selected_pet_name = st.selectbox("Which pet is this task for?", pet_names)
    selected_pet = next(p for p in owner.pets if p.name == selected_pet_name)

    col1, col2, col3 = st.columns(3)
    with col1:
        task_title = st.text_input("Task title", value="Morning walk")
    with col2:
        duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
    with col3:
        priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)

    if st.button("Add task"):
        selected_pet.add_task(
            Task(
                id=st.session_state.next_task_id,
                description=task_title,
                duration_mins=int(duration),
                priority=priority,
                due_time=datetime.now(),
            )
        )
        st.session_state.next_task_id += 1
        st.success(f"Added '{task_title}' to {selected_pet.name}.")

    all_tasks = owner.get_all_tasks()
    if all_tasks:
        st.write("Current tasks:")
        st.table(
            [
                {"Pet": pet.name, "Task": t.description, "Minutes": t.duration_mins, "Priority": t.priority}
                for pet, t in all_tasks
            ]
        )
    else:
        st.info("No tasks yet. Add one above.")

st.divider()

# --- Step 3: wire "Generate schedule" to Scheduler.generate_plan_for_owner() ---
st.subheader("Build Schedule")
available_mins = st.number_input(
    "Available time today (minutes)", min_value=1, max_value=720, value=60
)

if st.button("Generate schedule"):
    if not owner.get_all_tasks():
        st.info("Add at least one task above before generating a schedule.")
    else:
        plan = Scheduler().generate_plan_for_owner(owner, available_mins=int(available_mins))

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
