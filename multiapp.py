import streamlit as st

class MultiApp:
    def __init__(self):
        self.apps = []

    def add_page(self, title, func):
        """
        Adds a new page to the MultiApp
        """
        self.apps.append({
            "title": title,
            "function": func
        })

    def run(self):
        """
        Runtime method for the MultiApp
        """
        # Sidebar navigation
        st.sidebar.title("Navigation")
        app_selection = st.sidebar.radio(
            "Go To", 
            [app["title"] for app in self.apps]
        )

        # Run the selected app
        for app in self.apps:
            if app["title"] == app_selection:
                app["function"]()