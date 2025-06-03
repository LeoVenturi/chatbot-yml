import streamlit as st
from streamlit_option_menu import option_menu

from view import schermata_1

st.set_page_config(
    page_title="Pondering",
)

class Multiapp:

    def __init__(self):
        self.apps = []

    def add_app(self, title, function):
        self.apps.append({
            "title":title,
            "function":function
        })

    def run():

        with st.sidebar:
            app = option_menu(
            menu_title = None,
            options = ["Nuova conversazione"],
        )

        if app == "Nuova conversazione":
            schermata_1.app()

    run()

#streamlit run main.py