import streamlit as st
import os
from modules.data_ingestion import smart_loader
from modules.data_cleaner import clean_data

st.set_page_config(page_title="Data Ingestion", layout="wide")

st.title("📥 Data Ingestion")
st.markdown("---")

# 1. Source Selection Toggle
source_mode = st.radio("Select Data Source", ["Local CSV", "SQL Database (MySQL)"], horizontal=True)

# 2. Input Logic based on selection
if source_mode == "Local CSV":
    st.info("Ensure paths are entered as Raw Strings or use the file uploader for local testing.")
    
    # Dual approach: Path input for 20M+ rows (Spyder style) or Upload for smaller files
    input_method = st.selectbox("Input Method", ["File Uploader", "Direct File Path (Local)"])
    
    if input_method == "Direct File Path (Local)":
        raw_path = st.text_input("Enter Raw File Path:", placeholder=r"C:\Data\Production_Data.csv")
        if st.button("Load from Path"):
            with st.spinner("Processing High-Volume CSV..."):
                df = smart_loader("CSV", raw_path)
                if df is not None:
                    st.session_state['raw_data'], loss = clean_data(df)
                    st.success(f"Loaded successfully. Rows removed during cleaning: {loss}")
    else:
        uploaded_file = st.file_uploader("Upload CSV", type="csv")
        if uploaded_file:
            df = smart_loader("CSV", uploaded_file)
            st.session_state['raw_data'], loss = clean_data(df)
            st.success(f"File uploaded. Rows removed: {loss}")

elif source_mode == "SQL Database (MySQL)":
    st.warning("SQL Connection Mode: Currently in Beta. Ensure VPN/Firewall access is active.")
    
    col1, col2 = st.columns(2)
    with col1:
        host = st.text_input("Host Address", value="localhost")
        user = st.text_input("Username")
    with col2:
        database = st.text_input("Database Name")
        password = st.text_input("Password", type="password")
    
    query = st.text_area("SQL Query", placeholder="SELECT * FROM machine_data WHERE Line = 'A1'")
    
    if st.button("Execute Query"):
        db_config = {"host": host, "user": user, "password": password, "database": database}
        with st.spinner("Querying MySQL..."):
            df = smart_loader("SQL", query, db_config)
            if df is not None:
                st.session_state['raw_data'], loss = clean_data(df)
                st.success(f"Query successful. Rows removed: {loss}")

# 3. Data Preview & Metadata (SRS Section 5 Audit)
if 'raw_data' in st.session_state:
    st.markdown("---")
    st.subheader("Data Preview (The Golden Thread)")
    st.dataframe(st.session_state['raw_data'].head(100))
    
    st.metric("Total Active Rows", len(st.session_state['raw_data']))
    
    if st.button("Proceed to Diagnostics 🔗"):
        st.switch_page("pages/05_Diagnostics.py")
