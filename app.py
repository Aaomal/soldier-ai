import streamlit as st
from openai import OpenAI

st.set_page_config(page_title="Soldier AI", page_icon="🪖", layout="wide")

st.markdown("""
<style>
body {
    background-color: #0e1117;
    color: white;
}
</style>
""", unsafe_allow_html=True)
api_key = st.text_input("Enter API Key", type="password")

if not api_key:
    st.stop()

client = OpenAI(api_key=api_key)
if "messages" not in st.session_state:
    st.session_state.messages = []
    user_input = st.chat_input("Ask me anything...")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=st.session_state.messages
    )

    reply = response.choices[0].message.content

    st.session_state.messages.append({"role": "assistant", "content": reply})
    for msg in st.session_state.messages:
       if msg["role"] == "user":
        st.chat_message("user").write(msg["content"])
    else:
        st.chat_message("assistant").write(msg["content"])
        
