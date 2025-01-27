import streamlit as st
from multiapp import MultiApp
from pages import home, call_analysis, crm_insights, performance_tracking, deal  # Added deal import

def main():
    """
    Main Streamlit application with multi-page dashboard
    """
    st.set_page_config(
        page_title="Sentiment & Intent Analysis Deal Recommendations & Insights Hub AI-Powered Negotiation Coach Expected Outcomes",
        page_icon=":house:",
        layout="wide"
    )

    # Initialize MultiApp
    app = MultiApp()

    # Add pages
    app.add_page("Home", home.app)
    app.add_page("Call Analysis & Sentiment & Intent Analysis", call_analysis.app)
    app.add_page("CRM Insights", crm_insights.app)
    app.add_page("Performance Tracking", performance_tracking.app)
    app.add_page("Deal & Negotiation Recommendations  ", deal.app)  # Added Deal page

    # Run the app
    app.run()

if __name__ == "__main__":
    main()