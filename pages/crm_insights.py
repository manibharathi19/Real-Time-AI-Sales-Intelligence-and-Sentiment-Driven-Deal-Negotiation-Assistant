import streamlit as st
import pandas as pd
from crm_data_handler import load_crm_data
from config import CRM_FILE_PATH

def app():
    """
    CRM Insights page with data visualization and city search
    """
    st.title("CRM Data Insights")
    
    # Load CRM data
    crm_data = load_crm_data(CRM_FILE_PATH)
    
    if not crm_data.empty:
        # City search input
        st.subheader("Which City your looking for ?")
        city_input = st.text_input("Please enter the city name (currently, we support only Maharashtra):")
        
        # Filter data by city if input is provided
        if city_input:
            filtered_data = crm_data[crm_data['city'].str.contains(city_input, case=False, na=False)]
            
            if not filtered_data.empty:
                st.success(f"Found {len(filtered_data)} entries for {city_input}")
                st.dataframe(filtered_data)
                
                # Visualizations for filtered data
                try:
                    # Categorical column distribution
                    categorical_cols = filtered_data.select_dtypes(include=['object']).columns
                    if len(categorical_cols) > 0:
                        col1 = st.selectbox("Select Column for Distribution", categorical_cols)
                        st.subheader(f"Distribution of {col1}")
                        st.bar_chart(filtered_data[col1].value_counts())
                    
                    # Numeric column aggregation
                    numeric_cols = filtered_data.select_dtypes(include=['int64', 'float64']).columns
                    if len(numeric_cols) > 0:
                        col2 = st.selectbox("Select Numeric Column", numeric_cols)
                        st.subheader(f"Average {col2} by First Categorical Column")
                        
                        if len(categorical_cols) > 0:
                            st.bar_chart(filtered_data.groupby(categorical_cols[0])[col2].mean())
                
                except Exception as e:
                    st.error(f"Error creating visualizations: {e}")
            else:
                st.warning(f"No entries found for {city_input}")
        
        # # Original data overview
        # st.subheader("Full Data Overview")
        # st.dataframe(crm_data.head())
        
        # # Available columns
        # st.subheader("Available Columns")
        # st.write(crm_data.columns.tolist())