# crm_data_handler.py
import pandas as pd
import streamlit as st

def load_crm_data(filepath: str) -> pd.DataFrame:
    """
    Loads historical CRM data from a CSV file and normalizes column names.
    """
    try:
        data = pd.read_csv(filepath)
        data.columns = data.columns.str.strip().str.lower()  # Normalize column names
        st.success("CRM data loaded successfully.")
        return data
    except FileNotFoundError:
        st.error("CRM data file not found. Please upload the correct file.")
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Error loading CRM data: {e}")
        return pd.DataFrame()
