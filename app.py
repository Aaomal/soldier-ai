import streamlit as st
from openai import OpenAI
import json
import os

# -------------------------------------------------------------------
# PAGE CONFIG
# -------------------------------------------------------------------

st.set_page_config(
    page_title="Personal AI Coach & Companion",
    page_icon="🎖️",
    layout="centered"
)

# -------------------------------------------------------------------
# MEMORY FILE
# -------------------------------------------------------------------

MEMORY_FILE = "ai_companion_memory.json"

def load_memory():
    if os.path.exists(MEMORY_FILE):
        try:
            with open(MEMORY_FILE, "r") as f:
                return json.load(f)
        except:
            pass
    return {
        "coach_name": "Major Astra",
        "corrections": []
    }

def save_memory(data):
    with open(MEMORY_FILE, "w") as f:
        json.dump(data, f, indent=4)

memory_data = load_memory()

# -------------------------------------------------------------------
# SIDEBAR
# -------------------------------------------------------------------

st.sidebar.title("🎖️ Control Center")

api_key = st.sidebar.text_input("Enter API Key", type="password")

custom_name = st.sidebar.text_input(
    "AI Name:",
    value=memory_data.get("coach_name", "Major Astra")
)

if custom_name != memory_data.get("coach_name"):
    memory_data["coach_name"] = custom_name
    save_memory(memory_data)

st.sidebar.subheader("🧠 Teach AI")

new_rule = st.sidebar.text_area("Add rule:")

if st.sidebar.button("Save Rule"):
    if new_rule.strip():
        memory_data["corrections"].append(new_rule.strip())
        save_memory(memory_data)
        st.sidebar.success("Saved!")

# -------------------------------------------------------------------
# SYSTEM PROMPT
# -------------------------------------------------------------------

def build_system_prompt(name, corrections):
    lessons = "\n".join([f"- {c}" for c in corrections]) if corrections else "None"

    return f"""
You are {name}, an AI with 3 roles:

1. Friendly Companion
2. Expert Teacher
3. NDA Coach

Follow user rules:
{lessons}

Always explain clearly, step-by-step.
"""

# -------------------------------------------------------------------
# MAIN UI
# -------------------------------------------------------------------

st.title(f"🎖️ {custom_name}")
st.caption("Your AI Friend + Teacher + NDA Coach")

if "messages" not in st.session_state:
    st.session_state.messages = []

# show chat history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# user input
prompt = st.chat_input("Ask anything...")

if prompt:
    if not api_key:
        st.error("Enter API key in sidebar")
        st.stop()

    client = OpenAI(api_key=api_key)

    # add user message
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("user"):
        st.markdown(prompt)

    system_prompt = build_system_prompt(custom_name, memory_data["corrections"])

    full_messages = [{"role": "system", "content": system_prompt}] + st.session_state.messages

    # assistant response
    with st.chat_message("assistant"):
        placeholder = st.empty()
        full_response = ""

        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=full_messages,
                stream=True
            )

            for chunk in response:
                if chunk.choices[0].delta.content:
                    full_response += chunk.choices[0].delta.content
                    placeholder.markdown(full_response + "▌")

            placeholder.markdown(full_response)

        except Exception as e:
            st.error(f"Error: {e}")

    # save response
    st.session_state.messages.append({
        "role": "assistant",
        "content": full_response
    })
