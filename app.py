import streamlit as st
from auth import login_page

# 1. Global Page Settings (Must be the first Streamlit command)
st.set_page_config(page_title="XPDS Diagnostic Engine", layout="wide", page_icon="📊")

# 2. Session State for Authentication
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

# 3. Security Guard Logic
if not st.session_state.authenticated:
    # Hide the sidebar navigation until the user logs in
    st.markdown("""
        <style>
            [data-testid="stSidebarNav"] {display: none;}
        </style>
    """, unsafe_content_allowed=True)
    login_page()
else:
    # 4. Authenticated Landing Page
    st.title("📊 Diagnostic Engine Dashboard")
    
    # Welcome Section
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("""
        ### Welcome to the Technology Implementation Program (TIP)
        This platform provides a standardized interface for identifying process deviations.
        
        **Available Analytical Modules:**
        * 📥 **Ingestion:** Load CSV or SQL factory data.
        * 📈 **Visualization:** Inspect single-sensor stability and Cpk.
        * ⚖️ **Comparison:** Benchmark Machine A vs. Machine B.
        * 🔗 **Diagnostics:** Perform Time-Lag and Correlation analysis.
        """)
    
    with col2:
        st.info("👈 Use the sidebar to navigate between modules.")
        if st.button("Log Out"):
            st.session_state.authenticated = False
            st.rerun()

    st.divider()
    st.caption("XPDS Diagnostic Engine Baseline v1.5 | Confidential")
