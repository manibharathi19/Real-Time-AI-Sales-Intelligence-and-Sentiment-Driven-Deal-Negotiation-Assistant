import streamlit as st

def app():
    """
    Home dashboard page
    """
    st.title("Real Estate Deal Negotiation Dashboard")
    
    # Quick stats
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Calls", "52", "↑ 12 this month")
    
    with col2:
        st.metric("Conversion Rate", "68%", "↑ 5% from last month")
    
    with col3:
        st.metric("Avg Deal Value", "450K", "↑ 50K")

    # Recent Activities
    st.subheader("Recent Call Summaries")
    recent_summaries = [
        "Discussed property in Downtown with potential buyer",
        "Negotiation ongoing for suburban family home",
        "Client interested in investment property"
    ]
    
    for summary in recent_summaries:
        st.info(summary)
