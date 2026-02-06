import streamlit as st
from auth import login_page

st.set_page_config(page_title="XPDS Diagnostic Engine", layout="wide")

# Session State for Authentication
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    login_page()
else:
    st.title("📊 Diagnostic Engine Dashboard")
    st.sidebar.info("Select a module above to begin.")
    
    st.markdown("""
    ### Welcome to the Technology Implementation Program
    This platform analyzes cause-and-effect across:
    * **BTC** (Thermal Trends)
    * **Intensity/Distorted Glass** (Quality Patterns)
    * **Rejects** (Machine Stability)
    """)
