# app.py
import os
import json
from datetime import datetime
import streamlit as st

st.set_page_config(page_title="Chatbot UI (Streamlit)", page_icon="💬", layout="centered")

def init_state():
    if "messages" not in st.session_state:
        # default conversation with a friendly greeting
        st.session_state.messages = [
            {"role": "assistant", "content": "hi! i'm your chatbot. how can i help today?"}
        ]
    if "system_prompt" not in st.session_state:
        st.session_state.system_prompt = "you are a helpful, concise assistant."
    if "temperature" not in st.session_state:
        st.session_state.temperature = 0.3

def generate_reply(user_message: str, history: list[str], system_prompt: str, temperature: float) -> str:
    """
    Replace this with your model call.
    - 'history' is a list of "role: content" strings (oldest → newest).
    - Return a single string response.

    Example integration points:
      • OpenAI / Anthropic / local LLM server
      • RAG pipeline that augments 'history' with retrieved context
    """
    # --- DEMO fallback: simple echo with tiny "reasoning" riff ---
    return f"you said: {user_message}\n\n(temp={temperature}; messages so far={len(history)})"

def build_prompt_history(messages: list[dict], system_prompt: str) -> list[str]:
    """Flatten message dicts into readable lines for backends that want text history."""
    lines = [f"system: {system_prompt}"]
    for m in messages:
        lines.append(f"{m['role']}: {m['content']}")
    return lines

def download_json_button(label: str, data: dict, filename: str):
    st.download_button(
        label=label,
        data=json.dumps(data, ensure_ascii=False, indent=2),
        file_name=filename,
        mime="application/json",
        use_container_width=True,
    )

# -----------------------------
# Sidebar (settings)
# -----------------------------
init_state()
with st.sidebar:
    st.header("⚙️ settings")
    st.session_state.system_prompt = st.text_area(
        "system prompt",
        value=st.session_state.system_prompt,
        help="guides the assistant's behavior",
        height=120,
    )
    st.session_state.temperature = st.slider(
        "temperature", min_value=0.0, max_value=1.5, value=st.session_state.temperature, step=0.1,
        help="higher = more creative, lower = more precise",
    )
    st.divider()
    col_a, col_b = st.columns(2)
    with col_a:
        if st.button("🧹 reset chat", use_container_width=True):
            st.session_state.messages = []
            st.rerun()
    with col_b:
        if st.button("👋 new welcome", use_container_width=True):
            st.session_state.messages = [
                {"role": "assistant", "content": "hey again! what shall we tackle?"}
            ]
            st.rerun()
    st.divider()
    # export / import
    download_json_button(
        "⬇️ download transcript",
        {"messages": st.session_state.messages, "system_prompt": st.session_state.system_prompt},
        f"chat-{datetime.now().strftime('%Y%m%d-%H%M%S')}.json",
    )
    uploaded = st.file_uploader("⬆️ import transcript (.json)", type=["json"])
    if uploaded:
        try:
            data = json.load(uploaded)
            msgs = data.get("messages")
            sys_p = data.get("system_prompt", st.session_state.system_prompt)
            if isinstance(msgs, list) and all(isinstance(m, dict) for m in msgs):
                st.session_state.messages = msgs
                st.session_state.system_prompt = sys_p
                st.success("imported!")
                st.rerun()
            else:
                st.error("invalid transcript format")
        except Exception as e:
            st.error(f"failed to import: {e}")

# -----------------------------
# Header
# -----------------------------
st.title("💬 chatbot (streamlit)")
st.caption("drop-in UI scaffold — swap in your model inside `generate_reply()`.")

# -----------------------------
# Chat History
# -----------------------------
for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

# -----------------------------
# Chat Input & Response
# -----------------------------
user_input = st.chat_input("type your message…")
if user_input:
    # append user message first
    st.session_state.messages.append({"role": "user", "content": user_input})

    # display user bubble immediately
    with st.chat_message("user"):
        st.markdown(user_input)

    # prepare backend call
    history_lines = build_prompt_history(st.session_state.messages, st.session_state.system_prompt)

    # get assistant reply (replace this with your LLM call)
    assistant_text = generate_reply(
        user_message=user_input,
        history=history_lines,
        system_prompt=st.session_state.system_prompt,
        temperature=st.session_state.temperature,
    )

    # display assistant bubble
    with st.chat_message("assistant"):
        st.markdown(assistant_text)

    # store assistant message in history
    st.session_state.messages.append({"role": "assistant", "content": assistant_text})

# -----------------------------
# Footer note
# -----------------------------
st.markdown(
    "<div style='text-align:center; opacity:0.7; font-size:0.9rem'>"
    "built with <a href='https://streamlit.io' target='_blank'>streamlit</a> • "
    "replace <code>generate_reply()</code> with your model"
    "</div>",
    unsafe_allow_html=True,
)
