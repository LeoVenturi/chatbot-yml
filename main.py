import streamlit as st
from streamlit_option_menu import option_menu
from langchain_core.chat_history import BaseChatMessageHistory                                                          
from langchain_community.chat_message_histories import ChatMessageHistory    

from view import chatbot 

st.set_page_config(
    page_title="Pondering",
)

# Inizializzo la Chat Sessions nel session state 
if "chat_sessions" not in st.session_state:
    st.session_state.chat_sessions = {"Chat 1": ChatMessageHistory()}                                                   
    st.session_state.current_chat = "Chat 1"                                                                            
    st.session_state.chat_titles = {"Chat 1": "New Chat"}                                                               
    st.session_state.file_uploaded = {}
    st.session_state.file_content = {}

class Multiapp:

    def __init__(self):
        self.apps = []

    def add_app(self, title, function):
        self.apps.append({
            "title":title,
            "function":function
        })

    def run():

        # Sidebar 
        with st.sidebar:

            st.header("Chats")

            chat_keys = list(st.session_state.chat_sessions.keys())                                                 # List of all chat sessions

            # Display each chat session with its title and delete option
            for chat_id in chat_keys:

                col1, col2 = st.columns([4, 1])                                                                     # Layout with two columns: one for title, one for delete button

                with col1:                                                                                          # Highlight the current chat session
                    if st.session_state.current_chat == chat_id:
                        st.markdown(f"**{st.session_state.chat_titles[chat_id]}**")                                 # Bold current chat title

                    else:                                                                                           # Button to switch between chat sessions
                        if st.button(st.session_state.chat_titles[chat_id], key=chat_id):
                            st.session_state.current_chat = chat_id                                                 # Set selected chat as the current one
                            st.rerun()                                                                              # Refresh the page to show the new chat


                with col2:                                                                                          # Button to delete a chat session

                    if st.button("❌", key=f"delete_{chat_id}"):

                        del st.session_state.chat_sessions[chat_id]                                                 # Remove the chat session
                        del st.session_state.chat_titles[chat_id]                                                   # Remove the chat title

                        if st.session_state.current_chat == chat_id:                                                # If deleted chat was the current chat, switch to another one or create a new one

                            if st.session_state.chat_sessions:
                                st.session_state.current_chat = next(iter(st.session_state.chat_sessions))          # Select first chat

                            else:                                                                                   # If no chats remain, create a new default chat
                                st.session_state.chat_sessions["Chat 1"] = ChatMessageHistory()
                                st.session_state.chat_titles["Chat 1"] = "New Chat"
                                st.session_state.current_chat = "Chat 1"
                        st.rerun()                                                                                  # Refresh UI after deletion
  
            if st.button("➕ Nuova Chat"):                                                                          # Button to create a new chat session

                new_chat_id = f"Chat {len(st.session_state.chat_sessions) + 1}"                                     # Generate a new unique chat ID
                st.session_state.chat_sessions[new_chat_id] = ChatMessageHistory()                                  # Initialize the new chat history
                st.session_state.chat_titles[new_chat_id] = "New Chat"                                              # Set a default title for the new chat
                st.session_state.current_chat = new_chat_id                                                         # Set the new chat as the current chat
                st.rerun()    

        chatbot.app()                                                                            

    run()

#               streamlit run main.py