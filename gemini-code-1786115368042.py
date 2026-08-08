import streamlit as st
import json
import os
from openai import OpenAI

# -------------------------------------------------------------------
# Page Config (Mobile-Responsive & Clean UI)
# -------------------------------------------------------------------
st.set_page_config(
    page_title="Personal AI Coach & Companion",
    page_icon="🎖️",
    layout="centered",
    initial_sidebar_state="expanded"
)

MEMORY_FILE = "ai_companion_memory.json"

# -------------------------------------------------------------------
# Persistent Memory Engine (Learns from Mistakes & Preferences)
# -------------------------------------------------------------------
def load_memory():
    if os.path.exists(MEMORY_FILE):
        try:
            with open(MEMORY_FILE, "r") as f:
                return json.load(f)
        except Exception:
            pass
    return {
        "coach_name": "Major Astra",
        "corrections": [],
        "user_notes": []
    }

def save_memory(data):
    with open(MEMORY_FILE, "w") as f:
        json.dump(data, f, indent=4)

memory_data = load_memory()

# -------------------------------------------------------------------
# Sidebar: Customization & Memory Management
# -------------------------------------------------------------------
st.sidebar.title("🎖️ Control Center")

# 1. API Key Config
api_key = st.sidebar.text_input(
    "OpenAI / Compatible API Key", 
    type="password", 
    value=os.getenv("OPENAI_API_KEY", "")
)

# 2. Custom Naming
custom_name = st.sidebar.text_input(
    "Name Your AI Assistant:", 
    value=memory_data.get("coach_name", "Major Astra")
)
if custom_name != memory_data.get("coach_name"):
    memory_data["coach_name"] = custom_name
    save_memory(memory_data)
    st.sidebar.success(f"Renamed to {custom_name}!")

st.sidebar.divider()

# 3. Learn From Mistakes Engine
st.sidebar.subheader("🧠 Teach & Correct AI")
st.sidebar.caption("Add corrections or specific personal rules here so your AI never repeats a mistake.")

new_correction = st.sidebar.text_area(
    "Add a correction/rule:", 
    placeholder="e.g., Explain NDA calculus using geometric intuition first."
)
if st.sidebar.button("Save Lesson"):
    if new_correction.strip():
        memory_data["corrections"].append(new_correction.strip())
        save_memory(memory_data)
        st.sidebar.success("Rule saved permanently!")

if memory_data["corrections"]:
    with st.sidebar.expander("📚 Saved Memory Log"):
        for idx, corr in enumerate(memory_data["corrections"], 1):
            st.write(f"**{idx}.** {corr}")
        if st.button("Reset Saved Memory"):
            memory_data["corrections"] = []
            save_memory(memory_data)
            st.rerun()

# -------------------------------------------------------------------
# Triple-Identity System Prompt Engine
# -------------------------------------------------------------------
def build_system_prompt(name, corrections):
    lessons_formatted = "\n".join([f"- {c}" for c in corrections]) if corrections else "None yet."

    return f"""
You are '{name}', a versatile AI designed as a 3-in-1 personal assistant: a Friendly Companion, an NDA Exam Coach, and a Master Teacher.

### YOUR TRIPLE IDENTITY:

1. THE FRIENDLY COMPANION (Everyday Life & Support):
- Be warm, empathetic, relatable, and approachable.
- Chat naturally about daily life, stress, hobbies, general questions, or non-exam topics.
- Listen actively when the cadet feels burnt out, tired, or needs a sounding board.

2. THE EXPERT TEACHER (Conceptual Mastery & Clarification):
- Break down complex subjects (Mathematics, Physics, Chemistry, English, Geography, History, Polity) into crystal-clear logic.
- For math and science questions: Solve STEP-BY-STEP. State formulas clearly before using them.
- Avoid dumping bare answers—always explain the underlying 'why' and core concept.

3. THE DISCIPLINED NDA COACH (Strategy, Drills & Professionalism):
- Maintain military-grade precision, professionalism, and high standards.
- Enforce NDA exam awareness: Keep negative marking in mind (-0.83 for Math, -0.33 for GAT).
- Provide SSB interview preparation guidance (OIR tests, PPDT, Lecturette, personal interview tips).
- Manage information logically: Use bullet points, bold text, and clean formatting for study schedules or action plans.
- Address the user respectfully as "Cadet" or "Future Officer" when on NDA/exam topics.

### STRICT MEMORY RULES & PAST CORRECTIONS:
You MUST follow these rules taught by the user from previous sessions:
{lessons_formatted}
"""

# -------------------------------------------------------------------
# Main Chat Interface
# -------------------------------------------------------------------
st.title(f"🎖️ {custom_name}")
st.caption("Your All-in-One Friend, Master Teacher & NDA Preparation Coach.")

if "messages" not in st.session_state:
    st.session_state.messages = []

# Display history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# User Input
if prompt := st.chat_input("Ask a question, request a step-by-step solution, or just chat..."):
    if not api_key:
        st.error("Please enter your API Key in the sidebar to begin.")
        st.stop()

    client = OpenAI(api_key=api_key)

    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Build prompt and complete message history
    system_prompt = build_system_prompt(custom_name, memory_data["corrections"])
    full_messages = [{"role": "system", "content": system_prompt}] + [
        {"role": m["role"], "content": m["content"]} for m in st.session_state.messages
    ]

    # Generate Streamed Response
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""

        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=full_messages,
                temperature=0.4,
                stream=True
            )

            for chunk in response:
                if chunk.choices[0].delta.content:
                    full_response += chunk.choices[0].delta.content
                    message_placeholder.markdown(full_response + "▌")

            message_placeholder.markdown(full_response)

        except Exception as e:
            st.error(f"Error connecting to backend: {e}")

    if full_response:
        st.session_state.messages.append({"role": "assistant", "content": full_response})