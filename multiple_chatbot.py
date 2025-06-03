import streamlit as st                                              
import google.generativeai as genai     
from langchain_google_genai import ChatGoogleGenerativeAI                          
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage                                              
from langchain_core.output_parsers import StrOutputParser           
import os
from dotenv import load_dotenv                                      
import time        
from operator import itemgetter                                                                                         
from langchain_core.chat_history import BaseChatMessageHistory                                                          
from langchain_community.chat_message_histories import ChatMessageHistory                                               
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder                                              
from langchain_core.runnables import RunnablePassthrough                                                                



load_dotenv()


model = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash",  
    temperature=0,
    google_api_key=os.getenv("GEMINI_API_KEY"),
)


prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful assistant. Answer all questions to the best of your ability."),                       # Definisco il prompt base del chatbot
    MessagesPlaceholder(variable_name="messages"),
])


title_prompt = ChatPromptTemplate.from_messages([
    ("system", "Generate a short and relevant title for a conversation based on the given message."),                   # Definisco il prompt per generare il titolo
    ("human", "{message}"),
])


chain = (RunnablePassthrough.assign(messages=itemgetter("messages")) | prompt | model)        # Definisco il processo della catena: applico il prompt, faccio andare il model e passo la risposta
                                                                                                                      


# Inizializzo la Chat Sessions nel session state 
if "chat_sessions" not in st.session_state:
    st.session_state.chat_sessions = {"Chat 1": ChatMessageHistory()}                                                   
    st.session_state.current_chat = "Chat 1"                                                                            
    st.session_state.chat_titles = {"Chat 1": "New Chat"}                                                               
    st.session_state.file_uploaded = {}
    st.session_state.file_content = {}


# Funzione per avere la chat history della sessione
def get_session_history(session_id: str) -> BaseChatMessageHistory:
    
    if session_id not in st.session_state.chat_sessions:                                     # Se la sessione non esiste ne crea una nuova e inizializza la sua message history
        st.session_state.chat_sessions[session_id] = ChatMessageHistory()
        st.session_state.chat_titles[session_id] = "New Chat"
        st.session_state.file_uploaded[session_id] = False
        st.session_state.file_content[session_id] = ""
    return st.session_state.chat_sessions[session_id]


# Funzione per estrarre i dati dal file
def extract_text_from_file(uploaded_file):
    yaml_bytes = uploaded_file.read()
    yaml_str = yaml_bytes.decode('utf-8') 
    return yaml_str


# Funzione per avere un'animazione parola per parola delle risposte
def response_generator(text):
    for word in text.split():
        yield word + " "
        time.sleep(0.05)  



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
        st.rerun()                                                                                          # Refresh to update the UI with the new chat



# Main Chat UI
st.title("Multi-Chat Chatbot")

# Retrieve current chat history for the active chat session
current_chat_id = st.session_state.current_chat
chat_history = get_session_history(current_chat_id)


# Upload prompt
if not st.session_state.file_uploaded.get(current_chat_id):

    uploaded_file = st.file_uploader(label = 'Carica il file yaml', type = ["yaml", "yml"])

    if uploaded_file:

        file_text = extract_text_from_file(uploaded_file)
        st.session_state.file_uploaded[current_chat_id] = True
        st.session_state.file_content[current_chat_id] = file_text

        message = [
            SystemMessage(content="Descrivi a parole il contenuto dato senza ricopiarlo. In particolare descrivi il terzo livello di cartelle " \
            "figlie partendo dalla cartella root indicando il loro funzionamento e di cosa si occupano e senza elencarne i metodi"),
            HumanMessage(content=file_text)
        ]

        
        res = chain.invoke({"messages": message})                                                           # Invoke the chain to get AI response
        res_text = res.content                                                                              # Extract the AI response


        with st.chat_message("assistant"):
            res_placeholder = st.empty()
            response = ""
            for partial_response in response_generator(res_text):
                response += partial_response
                res_placeholder.markdown(response)                                                          # Update the displayed response
            res_placeholder.markdown(res_text)                                                              # Final display of complete response

        chat_history.add_message(res)                                                                       # Add message to chat history


        # Generate and set the chat title based on the first user message (if it's a new chat)
        if st.session_state.chat_titles[st.session_state.current_chat] == "New Chat":
            title_response = model.invoke([
                SystemMessage(content="Generate a short and relevant title starting from title of the uploaded file. USE THE SMALLEST NUMBER OF RELEVANT WORDS"),
                HumanMessage(content=file_text)
            ])
            generated_title = title_response.content.strip() if title_response else "Chat"
            st.session_state.chat_titles[st.session_state.current_chat] = generated_title                   # Set generated title
            st.rerun()                                                                                      # Refresh UI to display the new title

            st.success("File uploaded successfully! You can now start chatting.")
            st.rerun()

    else:
        st.info("Please upload a file to begin.")
        st.stop()



# Display previous chat messages
for message in chat_history.messages:
    with st.chat_message("user" if isinstance(message, HumanMessage) else "assistant"):
        st.markdown(message.content)


# Input field for user message
if prompt_text := st.chat_input("Enter your message..."):


    # Display user's message in the chat
    st.chat_message("user").markdown(prompt_text)
    user_message = HumanMessage(content=prompt_text)                                                        # Create a HumanMessage object
    chat_history.add_message(user_message)                                                                  # Add the user's message to the chat history


    # Prepare full prompt with file context
    file_context = st.session_state.file_content.get(current_chat_id, "")[:8000]
    
    messages = [
        SystemMessage(content="You are a helpful assistant. Answer all questions to the best of your ability."),
        SystemMessage(content=f"The user uploaded the following document:\n\n{file_context}"),
        *chat_history.messages
    ]

    
    response = chain.invoke({"messages": messages})                                                         # Invoke the chain to get AI response
    response_text = response.content                                                                        # Extract the AI response


    # Display AI response with animation
    with st.chat_message("assistant"):

        response_placeholder = st.empty()
        response = ""

        for partial_response in response_generator(response_text):
            response += partial_response
            response_placeholder.markdown(response)                                                         # Update the displayed response

        response_placeholder.markdown(response_text)                                                        # Final display of complete response


    # Add AI response to the chat history
    ai_message = AIMessage(content=response_text)
    chat_history.add_message(ai_message)


#   streamlit run multiple_chat_2.py