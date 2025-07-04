# app_logic.py
import os
import json
from llm.llm_query import get_response_from_llm

SESSION_LOG_DIR = "session_logs"

# Ensure the session log directory exists
os.makedirs(SESSION_LOG_DIR, exist_ok=True)

def get_session_filepath(session_id):
    return os.path.join(SESSION_LOG_DIR, f"{session_id}.json")

def load_chat_history(session_id):
    filepath = get_session_filepath(session_id)
    if os.path.exists(filepath):
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_chat_history(session_id, history):
    filepath = get_session_filepath(session_id)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(history, f, indent=2)

def handle_user_query(user_input, session_id="guest"):
    # Load previous messages
    history = load_chat_history(session_id)

    # Add system prompt as first message
    messages = [{"role": "system", "content": open("prompts/system_prompt.txt", "r", encoding="utf-8").read()}]
    messages += history
    messages.append({"role": "user", "content": user_input})

    # Get response
    assistant_reply = get_response_from_llm(messages)

    # Update history
    history.append({"role": "user", "content": user_input})
    history.append({"role": "assistant", "content": assistant_reply})
    save_chat_history(session_id, history)

    return assistant_reply, history  # history is list of dicts (for type='messages')

def list_sessions():
    """List all saved session IDs (excluding extension)."""
    files = sorted(os.listdir(SESSION_LOG_DIR), reverse=True)
    return [f.replace(".json", "") for f in files if f.endswith(".json")]

def load_session_history(session_id):
    """Load chat history as tuples (user, assistant) for chatbot display."""
    history = load_chat_history(session_id)
    formatted = []
    for i in range(0, len(history), 2):
        if i + 1 < len(history):
            user_msg = history[i].get("content", "")
            assistant_msg = history[i + 1].get("content", "")
            formatted.append((user_msg, assistant_msg))
    return formatted

def clear_session(session_id):
    """Clear the chat history for a specific session."""
    filepath = get_session_filepath(session_id)
    if os.path.exists(filepath):
        os.remove(filepath)
    return f"Session {session_id} cleared."
