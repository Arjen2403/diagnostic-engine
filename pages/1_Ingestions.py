import streamlit as st
import os
from modules.data_ingestion import smart_loader
from modules.data_cleaner import clean_data

st.set_page_config(page_title="Data Ingestion", layout="wide")

# Helper function to validate the thread visually
def validate_thread_ui(df):
    required = ['DateTimeID', 'Line', 'SectionPosition', 'GobPosition', 'Cavity']
    missing = [col for col in required if col not in df.columns]
    if not missing:
        st.success("Golden Thread Validated: Data is ready for Diagnostics. ✅")
    else:
        st.error(f"Missing Thread Keys: {missing}. Analytics may fail. ❌")

st.title("📥 Data Ingestion")
st.markdown("---")

source_mode = st.radio("Select Data Source", ["Local CSV", "SQL Database (MySQL)"], horizontal=True)

if source_mode == "Local CSV":
    input_method = st.selectbox("Input Method", ["File Uploader", "Direct File Path (Local)"])
    
    if input_method == "Direct File Path (Local)":
        raw_path = st.text_input("Enter Raw File Path:", placeholder=r"C:\Data\Production_Data.csv")
        if st.button("Load from Path"):
            with st.spinner("Processing High-Volume CSV..."):
                df = smart_loader("CSV", raw_path)
                if df is not None:
                    st.session_state['raw_data'], loss = clean_data(df)
                    st.success(f"Loaded successfully. Rows removed: {loss}")
    else:
        uploaded_file = st.file_uploader("Upload CSV", type="csv")
        if uploaded_file:
            df = smart_loader("CSV", uploaded_file)
            st.session_state['raw_data'], loss = clean_data(df)
            st.success(f"File uploaded. Rows removed: {loss}")

# (SQL logic remains same but calls the same validation below)

if 'raw_data' in st.session_state:
    st.markdown("---")
    validate_thread_ui(st.session_state['raw_data'])
    
    st.subheader("Data Preview")
    st.dataframe(st.session_state['raw_data'].head(50))
    
    st.metric("Total Active Rows", len(st.session_state['raw_data']))
    
    # Logic Fix: Ensuring the path works for all Streamlit launch methods
    if st.button("Proceed to Diagnostics 🔗"):
        st.switch_page("pages/05_Diagnostics.py")
