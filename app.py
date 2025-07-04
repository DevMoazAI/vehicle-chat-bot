import gradio as gr
from app_logic import handle_user_query, clear_session
import uuid
import os
import json

SESSION_LOG_DIR = "session_logs"
METADATA_DIR = "chat_metadata"
os.makedirs(SESSION_LOG_DIR, exist_ok=True)
os.makedirs(METADATA_DIR, exist_ok=True)

# Create new session ID
session_id = str(uuid.uuid4())[:8]

# Load list of previous session files with their display names
def list_sessions():
    sessions = []
    for f in os.listdir(SESSION_LOG_DIR):
        if f.endswith(".json") and not f.endswith("_metadata.json"):  # Exclude metadata files
            session_id = f.replace(".json", "")
            # Skip invalid session IDs
            if session_id in ["[]", "", "null"]:
                continue
            # Try to load custom name from metadata
            display_name = get_session_display_name(session_id)
            sessions.append((display_name, session_id))  # (display_name, session_id)
    return sessions

def get_session_display_name(session_id):
    """Get the display name for a session (custom name or default)"""
    metadata_path = os.path.join(METADATA_DIR, f"{session_id}_metadata.json")
    if os.path.exists(metadata_path):
        try:
            with open(metadata_path, "r", encoding="utf-8") as f:
                metadata = json.load(f)
                return metadata.get("display_name", session_id)
        except:
            pass
    return session_id  # Default to session ID if no custom name

def save_session_metadata(session_id, display_name):
    """Save custom display name for a session"""
    metadata_path = os.path.join(METADATA_DIR, f"{session_id}_metadata.json")
    metadata = {"display_name": display_name}
    with open(metadata_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)

def get_radio_choices():
    """Get formatted choices for radio component"""
    sessions = list_sessions()
    choices = []
    for display_name, session_id in sessions:
        # Always show only the display name (custom name or session ID)
        choices.append(display_name)
    return choices

def extract_session_id_from_choice(choice):
    """Extract session ID from radio choice"""
    # Since we only show display names, we need to find the actual session ID
    sessions = list_sessions()
    for display_name, session_id in sessions:
        if display_name == choice:
            return session_id
    return choice  # Fallback if not found

with gr.Blocks() as demo:
    with gr.Row():
        with gr.Column(scale=1):
            gr.Markdown("##  Previous Chats")
            chat_list = gr.Radio(choices=get_radio_choices(), label="Your Chats", interactive=True)
            
            with gr.Row():
                new_chat_btn = gr.Button(" New Chat", scale=1)
                refresh_btn = gr.Button(" Refresh", scale=1)
            
            # Rename section
            gr.Markdown("### Rename Selected Chat")
            rename_input = gr.Textbox(label="New Name", placeholder="Enter new chat name...")
            rename_btn = gr.Button("Rename Chat")
            rename_status = gr.Textbox(label="Status", interactive=False, visible=False)
            
        with gr.Column(scale=4):
            gr.Markdown("##  Vehicle Diagnostic Chatbot")
            chatbot = gr.Chatbot(label="Vehicle Diagnostic Assistant", type="messages")
            msg = gr.Textbox(label="Your Question", placeholder="Describe your vehicle issue...")
            state = gr.State([])

    def chat_fn(user_message, history):
        response, full_history = handle_user_query(user_message, session_id=session_id)
        return full_history, full_history, ""  # Clear the textbox after submission

    def clear_chat():
        """Start a new chat session"""
        global session_id
        session_id = str(uuid.uuid4())[:8]  # Generate new session ID
        clear_session(session_id)
        return [], [], None  # Return None to clear radio selection

    def refresh_sessions():
        """Refresh the list of available sessions"""
        return gr.Radio(choices=get_radio_choices(), value=None)

    def load_chat(chat_choice):
        """Load a previous chat session"""
        if chat_choice is None:
            return [], []
        
        session_id = extract_session_id_from_choice(chat_choice)
        path = os.path.join(SESSION_LOG_DIR, f"{session_id}.json")
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                history = json.load(f)
            return history, history
        return [], []

    def rename_chat(chat_choice, new_name):
        """Rename a chat session"""
        if not chat_choice:
            return "Error: Please select a chat to rename", gr.Radio(choices=get_radio_choices(), value=None), "", gr.Textbox(visible=True)
        
        if not new_name or not new_name.strip():
            return "Error: Please enter a new name", gr.Radio(choices=get_radio_choices(), value=chat_choice), new_name, gr.Textbox(visible=True)
        
        session_id = extract_session_id_from_choice(chat_choice)
        
        # Check if session exists
        session_path = os.path.join(SESSION_LOG_DIR, f"{session_id}.json")
        if not os.path.exists(session_path):
            return "Error: Chat session not found", gr.Radio(choices=get_radio_choices(), value=None), "", gr.Textbox(visible=True)
        
        # Save the new name
        save_session_metadata(session_id, new_name.strip())
        
        # Update radio choices and select the renamed item
        updated_choices = get_radio_choices()
        new_choice = new_name.strip()  # Just use the new name, not with session ID
        
        return "Success: Chat renamed successfully!", gr.Radio(choices=updated_choices, value=new_choice), "", gr.Textbox(visible=True)

    def hide_rename_status():
        """Hide the rename status after a delay"""
        return gr.Textbox(visible=False)

    def handle_status_change(status_msg):
        """Handle status message changes safely"""
        if status_msg and isinstance(status_msg, str) and status_msg.startswith("Success:"):
            return gr.Textbox(visible=False)
        return gr.Textbox(visible=True)

    # Event handlers
    msg.submit(chat_fn, [msg, state], [chatbot, state, msg])
    new_chat_btn.click(clear_chat, None, [chatbot, state, chat_list])
    refresh_btn.click(refresh_sessions, None, [chat_list])
    chat_list.change(load_chat, chat_list, [chatbot, state])
    rename_btn.click(rename_chat, [chat_list, rename_input], [rename_status, chat_list, rename_input, rename_status])
    
    # Hide status message after showing success
    rename_status.change(handle_status_change, rename_status, rename_status)

demo.launch()



















# import gradio as gr
# from app_logic import handle_user_query, clear_session
# import uuid
# import os
# import json

# SESSION_LOG_DIR = "session_logs"
# METADATA_DIR = "chat_metadata"
# os.makedirs(SESSION_LOG_DIR, exist_ok=True)
# os.makedirs(METADATA_DIR, exist_ok=True)

# # Create new session ID
# session_id = str(uuid.uuid4())[:8]

# # Load list of previous session files with their display names
# def list_sessions():
#     sessions = []
#     for f in os.listdir(SESSION_LOG_DIR):
#         if f.endswith(".json") and not f.endswith("_metadata.json"):  # Exclude metadata files
#             session_id = f.replace(".json", "")
#             # Skip invalid session IDs
#             if session_id in ["[]", "", "null"]:
#                 continue
#             # Try to load custom name from metadata
#             display_name = get_session_display_name(session_id)
#             sessions.append((display_name, session_id))  # (display_name, session_id)
#     return sessions

# def get_session_display_name(session_id):
#     """Get the display name for a session (custom name or default)"""
#     metadata_path = os.path.join(METADATA_DIR, f"{session_id}_metadata.json")
#     if os.path.exists(metadata_path):
#         try:
#             with open(metadata_path, "r", encoding="utf-8") as f:
#                 metadata = json.load(f)
#                 return metadata.get("display_name", session_id)
#         except:
#             pass
#     return session_id  # Default to session ID if no custom name

# def save_session_metadata(session_id, display_name):
#     """Save custom display name for a session"""
#     metadata_path = os.path.join(METADATA_DIR, f"{session_id}_metadata.json")
#     metadata = {"display_name": display_name}
#     with open(metadata_path, "w", encoding="utf-8") as f:
#         json.dump(metadata, f, ensure_ascii=False, indent=2)

# def get_radio_choices():
#     """Get formatted choices for radio component"""
#     sessions = list_sessions()
#     choices = []
#     for display_name, session_id in sessions:
#         # Always show only the display name (custom name or session ID)
#         choices.append(display_name)
#     return choices

# def extract_session_id_from_choice(choice):
#     """Extract session ID from radio choice"""
#     # Since we only show display names, we need to find the actual session ID
#     sessions = list_sessions()
#     for display_name, session_id in sessions:
#         if display_name == choice:
#             return session_id
#     return choice  # Fallback if not found

# with gr.Blocks() as demo:
#     with gr.Row():
#         with gr.Column(scale=1):
#             gr.Markdown("##  Previous Chats")
#             chat_list = gr.Radio(choices=get_radio_choices(), label="Your Chats", interactive=True)
            
#             with gr.Row():
#                 new_chat_btn = gr.Button(" New Chat", scale=1)
#                 refresh_btn = gr.Button(" Refresh", scale=1)
            
#             # Rename section
#             gr.Markdown("### Rename Selected Chat")
#             rename_input = gr.Textbox(label="New Name", placeholder="Enter new chat name...")
#             rename_btn = gr.Button(" Rename Chat")
#             rename_status = gr.Textbox(label="Status", interactive=False, visible=False)
            
#         with gr.Column(scale=4):
#             gr.Markdown("##  Vehicle Diagnostic Chatbot")
#             chatbot = gr.Chatbot(label="Vehicle Diagnostic Assistant", type="messages")
#             msg = gr.Textbox(label="Your Question", placeholder="Describe your vehicle issue...")
#             state = gr.State([])

#     def chat_fn(user_message, history):
#         response, full_history = handle_user_query(user_message, session_id=session_id)
#         return full_history, full_history, ""  # Clear the textbox after submission

#     def clear_chat():
#         """Start a new chat session"""
#         global session_id
#         session_id = str(uuid.uuid4())[:8]  # Generate new session ID
#         clear_session(session_id)
#         return [], [], None  # Return None to clear radio selection

#     def refresh_sessions():
#         """Refresh the list of available sessions"""
#         return gr.Radio(choices=get_radio_choices(), value=None)

#     def load_chat(chat_choice):
#         """Load a previous chat session"""
#         if chat_choice is None:
#             return [], []
        
#         session_id = extract_session_id_from_choice(chat_choice)
#         path = os.path.join(SESSION_LOG_DIR, f"{session_id}.json")
#         if os.path.exists(path):
#             with open(path, "r", encoding="utf-8") as f:
#                 history = json.load(f)
#             return history, history
#         return [], []

#     def rename_chat(chat_choice, new_name):
#         """Rename a chat session"""
#         if not chat_choice:
#             return " Please select a chat to rename", gr.Radio(choices=get_radio_choices(), value=None), "", gr.Textbox(visible=True)
        
#         if not new_name or not new_name.strip():
#             return " Please enter a new name", gr.Radio(choices=get_radio_choices(), value=chat_choice), new_name, gr.Textbox(visible=True)
        
#         session_id = extract_session_id_from_choice(chat_choice)
        
#         # Check if session exists
#         session_path = os.path.join(SESSION_LOG_DIR, f"{session_id}.json")
#         if not os.path.exists(session_path):
#             return " Chat session not found", gr.Radio(choices=get_radio_choices(), value=None), "", gr.Textbox(visible=True)
        
#         # Save the new name
#         save_session_metadata(session_id, new_name.strip())
        
#         # Update radio choices and select the renamed item
#         updated_choices = get_radio_choices()
#         new_choice = new_name.strip()  # Just use the new name, not with session ID
        
#         return " Chat renamed successfully!", gr.Radio(choices=updated_choices, value=new_choice), "", gr.Textbox(visible=True)

#     def hide_rename_status():
#         """Hide the rename status after a delay"""
#         return gr.Textbox(visible=False)

#     # Event handlers
#     msg.submit(chat_fn, [msg, state], [chatbot, state, msg])
#     new_chat_btn.click(clear_chat, None, [chatbot, state, chat_list])
#     refresh_btn.click(refresh_sessions, None, [chat_list])
#     chat_list.change(load_chat, chat_list, [chatbot, state])
#     rename_btn.click(rename_chat, [chat_list, rename_input], [rename_status, chat_list, rename_input, rename_status])
    
#     # Hide status message after showing it
#     rename_status.change(lambda x: gr.Textbox(visible=False) if x.startswith("✅") else None, rename_status, rename_status)

# demo.launch()




























# import gradio as gr
# from app_logic import handle_user_query, clear_session
# import uuid
# import os
# import json

# SESSION_LOG_DIR = "session_logs"
# METADATA_DIR = "chat_metadata"
# os.makedirs(SESSION_LOG_DIR, exist_ok=True)
# os.makedirs(METADATA_DIR, exist_ok=True)

# # Create new session ID
# session_id = str(uuid.uuid4())[:8]

# # Load list of previous session files with their display names
# def list_sessions():
#     sessions = []
#     for f in os.listdir(SESSION_LOG_DIR):
#         if f.endswith(".json") and not f.endswith("_metadata.json"):  # Exclude metadata files
#             session_id = f.replace(".json", "")
#             # Try to load custom name from metadata
#             display_name = get_session_display_name(session_id)
#             sessions.append((display_name, session_id))  # (display_name, session_id)
#     return sessions

# def get_session_display_name(session_id):
#     """Get the display name for a session (custom name or default)"""
#     metadata_path = os.path.join(METADATA_DIR, f"{session_id}_metadata.json")
#     if os.path.exists(metadata_path):
#         try:
#             with open(metadata_path, "r", encoding="utf-8") as f:
#                 metadata = json.load(f)
#                 return metadata.get("display_name", session_id)
#         except:
#             pass
#     return session_id  # Default to session ID if no custom name

# def save_session_metadata(session_id, display_name):
#     """Save custom display name for a session"""
#     metadata_path = os.path.join(METADATA_DIR, f"{session_id}_metadata.json")
#     metadata = {"display_name": display_name}
#     with open(metadata_path, "w", encoding="utf-8") as f:
#         json.dump(metadata, f, ensure_ascii=False, indent=2)

# def get_radio_choices():
#     """Get formatted choices for radio component"""
#     sessions = list_sessions()
#     return [f"{display_name} ({session_id})" for display_name, session_id in sessions]

# def extract_session_id_from_choice(choice):
#     """Extract session ID from radio choice"""
#     if choice and "(" in choice and choice.endswith(")"):
#         return choice.split("(")[-1].rstrip(")")
#     return choice

# with gr.Blocks() as demo:
#     with gr.Row():
#         with gr.Column(scale=1):
#             gr.Markdown("##  Previous Chats")
#             chat_list = gr.Radio(choices=get_radio_choices(), label="Your Chats", interactive=True)
            
#             with gr.Row():
#                 new_chat_btn = gr.Button(" New Chat", scale=1)
#                 refresh_btn = gr.Button(" Refresh", scale=1)
            
#             # Rename section
#             gr.Markdown("### Rename Selected Chat")
#             rename_input = gr.Textbox(label="New Name", placeholder="Enter new chat name...")
#             rename_btn = gr.Button(" Rename Chat")
#             rename_status = gr.Textbox(label="Status", interactive=False, visible=False)
            
#         with gr.Column(scale=4):
#             gr.Markdown("##  Vehicle Diagnostic Chatbot")
#             chatbot = gr.Chatbot(label="Vehicle Diagnostic Assistant", type="messages")
#             msg = gr.Textbox(label="Your Question", placeholder="Describe your vehicle issue...")
#             state = gr.State([])

#     def chat_fn(user_message, history):
#         response, full_history = handle_user_query(user_message, session_id=session_id)
#         return full_history, full_history, ""  # Clear the textbox after submission

#     def clear_chat():
#         """Start a new chat session"""
#         global session_id
#         session_id = str(uuid.uuid4())[:8]  # Generate new session ID
#         clear_session(session_id)
#         return [], [], None  # Return None to clear radio selection

#     def refresh_sessions():
#         """Refresh the list of available sessions"""
#         return gr.Radio(choices=get_radio_choices(), value=None)

#     def load_chat(chat_choice):
#         """Load a previous chat session"""
#         if chat_choice is None:
#             return [], []
        
#         session_id = extract_session_id_from_choice(chat_choice)
#         path = os.path.join(SESSION_LOG_DIR, f"{session_id}.json")
#         if os.path.exists(path):
#             with open(path, "r", encoding="utf-8") as f:
#                 history = json.load(f)
#             return history, history
#         return [], []

#     def rename_chat(chat_choice, new_name):
#         """Rename a chat session"""
#         if not chat_choice:
#             return " Please select a chat to rename", gr.Radio(choices=get_radio_choices(), value=None), "", gr.Textbox(visible=True)
        
#         if not new_name or not new_name.strip():
#             return " Please enter a new name", gr.Radio(choices=get_radio_choices(), value=chat_choice), new_name, gr.Textbox(visible=True)
        
#         session_id = extract_session_id_from_choice(chat_choice)
        
#         # Check if session exists
#         session_path = os.path.join(SESSION_LOG_DIR, f"{session_id}.json")
#         if not os.path.exists(session_path):
#             return " Chat session not found", gr.Radio(choices=get_radio_choices(), value=None), "", gr.Textbox(visible=True)
        
#         # Save the new name
#         save_session_metadata(session_id, new_name.strip())
        
#         # Update radio choices and select the renamed item
#         updated_choices = get_radio_choices()
#         new_choice = f"{new_name.strip()} ({session_id})"
        
#         return " Chat renamed successfully!", gr.Radio(choices=updated_choices, value=new_choice), "", gr.Textbox(visible=True)

#     def hide_rename_status():
#         """Hide the rename status after a delay"""
#         return gr.Textbox(visible=False)

#     # Event handlers
#     msg.submit(chat_fn, [msg, state], [chatbot, state, msg])
#     new_chat_btn.click(clear_chat, None, [chatbot, state, chat_list])
#     refresh_btn.click(refresh_sessions, None, [chat_list])
#     chat_list.change(load_chat, chat_list, [chatbot, state])
#     rename_btn.click(rename_chat, [chat_list, rename_input], [rename_status, chat_list, rename_input, rename_status])
    
#     # Hide status message after showing it
#     rename_status.change(lambda x: gr.Textbox(visible=False) if x.startswith("✅") else None, rename_status, rename_status)

# demo.launch()

























# # import gradio as gr
# # from app_logic import handle_user_query, clear_session
# # import uuid
# # import os
# # import json

# # SESSION_LOG_DIR = "session_logs"
# # os.makedirs(SESSION_LOG_DIR, exist_ok=True)

# # # Create new session ID
# # session_id = str(uuid.uuid4())[:8]

# # # Load list of previous session files
# # def list_sessions():
# #     return [f.replace(".json", "") for f in os.listdir(SESSION_LOG_DIR) if f.endswith(".json")]

# # with gr.Blocks() as demo:
# #     with gr.Row():
# #         with gr.Column(scale=1):
# #             gr.Markdown("##  Previous Chats")
# #             chat_list = gr.Radio(choices=list_sessions(), label="Your Chats", interactive=True)
# #             new_chat_btn = gr.Button(" New Chat")
# #             refresh_btn = gr.Button(" Refresh Sessions")
# #         with gr.Column(scale=4):
# #             gr.Markdown("##  Vehicle Diagnostic Chatbot")
# #             chatbot = gr.Chatbot(label="Vehicle Diagnostic Assistant", type="messages")
# #             msg = gr.Textbox(label="Your Question", placeholder="Describe your vehicle issue...")
# #             state = gr.State([])

# #     def chat_fn(user_message, history):
# #         response, full_history = handle_user_query(user_message, session_id=session_id)
# #         return full_history, full_history, ""  # Clear the textbox after submission

# #     def clear_chat():
# #         """Start a new chat session"""
# #         global session_id
# #         session_id = str(uuid.uuid4())[:8]  # Generate new session ID
# #         clear_session(session_id)
# #         return [], [], None  # Return None to clear radio selection

# #     def refresh_sessions():
# #         """Refresh the list of available sessions"""
# #         return gr.Radio(choices=list_sessions(), value=None)

# #     def load_chat(chat_id):
# #         """Load a previous chat session"""
# #         if chat_id is None:
# #             return [], []
        
# #         path = os.path.join(SESSION_LOG_DIR, f"{chat_id}.json")
# #         if os.path.exists(path):
# #             with open(path, "r", encoding="utf-8") as f:
# #                 history = json.load(f)
# #             return history, history
# #         return [], []

# #     # Event handlers
# #     msg.submit(chat_fn, [msg, state], [chatbot, state, msg])
# #     new_chat_btn.click(clear_chat, None, [chatbot, state, chat_list])
# #     refresh_btn.click(refresh_sessions, None, [chat_list])
# #     chat_list.change(load_chat, chat_list, [chatbot, state])

# # demo.launch()





# import gradio as gr
# from app_logic import handle_user_query, clear_session
# import uuid
# import os
# import json

# SESSION_LOG_DIR = "session_logs"
# os.makedirs(SESSION_LOG_DIR, exist_ok=True)

# # Create new session ID
# session_id = str(uuid.uuid4())[:8]

# # Load list of previous session files with their display names
# def list_sessions():
#     sessions = []
#     for f in os.listdir(SESSION_LOG_DIR):
#         if f.endswith(".json"):
#             session_id = f.replace(".json", "")
#             # Try to load custom name from metadata
#             display_name = get_session_display_name(session_id)
#             sessions.append((display_name, session_id))  # (display_name, session_id)
#     return sessions

# def get_session_display_name(session_id):
#     """Get the display name for a session (custom name or default)"""
#     metadata_path = os.path.join(SESSION_LOG_DIR, f"{session_id}_metadata.json")
#     if os.path.exists(metadata_path):
#         try:
#             with open(metadata_path, "r", encoding="utf-8") as f:
#                 metadata = json.load(f)
#                 return metadata.get("display_name", session_id)
#         except:
#             pass
#     return session_id  # Default to session ID if no custom name

# def save_session_metadata(session_id, display_name):
#     """Save custom display name for a session"""
#     metadata_path = os.path.join(SESSION_LOG_DIR, f"{session_id}_metadata.json")
#     metadata = {"display_name": display_name}
#     with open(metadata_path, "w", encoding="utf-8") as f:
#         json.dump(metadata, f, ensure_ascii=False, indent=2)

# def get_radio_choices():
#     """Get formatted choices for radio component"""
#     sessions = list_sessions()
#     return [f"{display_name} ({session_id})" for display_name, session_id in sessions]

# def extract_session_id_from_choice(choice):
#     """Extract session ID from radio choice"""
#     if choice and "(" in choice and choice.endswith(")"):
#         return choice.split("(")[-1].rstrip(")")
#     return choice

# with gr.Blocks() as demo:
#     with gr.Row():
#         with gr.Column(scale=1):
#             gr.Markdown("##  Previous Chats")
#             chat_list = gr.Radio(choices=get_radio_choices(), label="Your Chats", interactive=True)
            
#             with gr.Row():
#                 new_chat_btn = gr.Button(" New Chat", scale=1)
#                 refresh_btn = gr.Button(" Refresh", scale=1)
            
#             # Rename section
#             gr.Markdown("### Rename Selected Chat")
#             rename_input = gr.Textbox(label="New Name", placeholder="Enter new chat name...")
#             rename_btn = gr.Button(" Rename Chat")
#             rename_status = gr.Textbox(label="Status", interactive=False, visible=False)
            
#         with gr.Column(scale=4):
#             gr.Markdown("##  Vehicle Diagnostic Chatbot")
#             chatbot = gr.Chatbot(label="Vehicle Diagnostic Assistant", type="messages")
#             msg = gr.Textbox(label="Your Question", placeholder="Describe your vehicle issue...")
#             state = gr.State([])

#     def chat_fn(user_message, history):
#         response, full_history = handle_user_query(user_message, session_id=session_id)
#         return full_history, full_history, ""  # Clear the textbox after submission

#     def clear_chat():
#         """Start a new chat session"""
#         global session_id
#         session_id = str(uuid.uuid4())[:8]  # Generate new session ID
#         clear_session(session_id)
#         return [], [], None  # Return None to clear radio selection

#     def refresh_sessions():
#         """Refresh the list of available sessions"""
#         return gr.Radio(choices=get_radio_choices(), value=None)

#     def load_chat(chat_choice):
#         """Load a previous chat session"""
#         if chat_choice is None:
#             return [], []
        
#         session_id = extract_session_id_from_choice(chat_choice)
#         path = os.path.join(SESSION_LOG_DIR, f"{session_id}.json")
#         if os.path.exists(path):
#             with open(path, "r", encoding="utf-8") as f:
#                 history = json.load(f)
#             return history, history
#         return [], []

#     def rename_chat(chat_choice, new_name):
#         """Rename a chat session"""
#         if not chat_choice:
#             return " Please select a chat to rename", gr.Radio(choices=get_radio_choices(), value=None), "", gr.Textbox(visible=True)
        
#         if not new_name or not new_name.strip():
#             return " Please enter a new name", gr.Radio(choices=get_radio_choices(), value=chat_choice), new_name, gr.Textbox(visible=True)
        
#         session_id = extract_session_id_from_choice(chat_choice)
        
#         # Check if session exists
#         session_path = os.path.join(SESSION_LOG_DIR, f"{session_id}.json")
#         if not os.path.exists(session_path):
#             return " Chat session not found", gr.Radio(choices=get_radio_choices(), value=None), "", gr.Textbox(visible=True)
        
#         # Save the new name
#         save_session_metadata(session_id, new_name.strip())
        
#         # Update radio choices and select the renamed item
#         updated_choices = get_radio_choices()
#         new_choice = f"{new_name.strip()} ({session_id})"
        
#         return " Chat renamed successfully!", gr.Radio(choices=updated_choices, value=new_choice), "", gr.Textbox(visible=True)

#     def hide_rename_status():
#         """Hide the rename status after a delay"""
#         return gr.Textbox(visible=False)

#     # Event handlers
#     msg.submit(chat_fn, [msg, state], [chatbot, state, msg])
#     new_chat_btn.click(clear_chat, None, [chatbot, state, chat_list])
#     refresh_btn.click(refresh_sessions, None, [chat_list])
#     chat_list.change(load_chat, chat_list, [chatbot, state])
#     rename_btn.click(rename_chat, [chat_list, rename_input], [rename_status, chat_list, rename_input, rename_status])
    
#     # Hide status message after showing it
#     rename_status.change(lambda x: gr.Textbox(visible=False) if x.startswith("✅") else None, rename_status, rename_status)

# demo.launch()