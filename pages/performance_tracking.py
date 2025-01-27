import streamlit as st
import pandas as pd

def app():
    """
    Performance Tracking page
    """
    st.title("Agent Performance Dashboard")
    
    # Mock performance data
    performance_data = pd.DataFrame({
        'Agent': ['Mani', 'Sai', 'mahima', 'Thaheer','ezhil'],
        'Calls Made': [20, 15, 10, 5, 1],
        'Conversion Rate': [0.65, 0.72, 0.58, 0.68 , 0.78],
        'Total Deal Value': [350000, 480000, 275000, 420000,1000000]
    })
    
    st.dataframe(performance_data)
    
    # Performance Charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Calls Made")
        st.bar_chart(performance_data.set_index('Agent')['Calls Made'])
    
    with col2:
        st.subheader("Conversion Rate")
        st.bar_chart(performance_data.set_index('Agent')['Conversion Rate'])