from google import genai
from google.genai import types
import streamlit as st
from langchain.memory import ChatMessageHistory


def app():
    client = genai.Client(api_key='AIzaSyB0KNflRgR6VcsSA-_OeW5GUJnbRYHwda8')

    st.title("App Test")

    df = st.file_uploader(label = 'Carica il file yaml', type = ["yaml", "yml"])

    if df:

        yaml_bytes = df.read()
        yaml_str = yaml_bytes.decode('utf-8') 

        def get_session_history(session_id: str, chat_sessions: dict, chat_titles: dict) -> ChatMessageHistory:
            if session_id not in chat_sessions:
                chat_sessions[session_id] = ChatMessageHistory()
                chat_titles[session_id] = "New Chat"

            return chat_sessions[session_id]   
        
        
        prompt = yaml_str

        response = client.models.generate_content(
            model = 'gemini-2.0-flash',
            config=types.GenerateContentConfig(
                system_instruction = "Descrivi a parole il contenuto dato senza ricopiarlo. In particolare descrivi il terzo livello di cartelle figlie partendo dalla cartella root indicando il loro funzionamento e di cosa si occupano e senza elencarne i metodi"),
            contents = prompt)

        submitted = st.button("Response")

        if submitted:
            st.subheader("Summary:")
            st.write(response.text)


