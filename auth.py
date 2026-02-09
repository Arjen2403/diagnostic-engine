import streamlit as st

def login_page():
    """
    Standard Authentication Layer for TIP Projects.
    """
    st.title("🔐 TIP Diagnostic Engine Login")
    
    # Create a centered login form
    with st.container():
        st.subheader("Please sign in to continue")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        
        if st.button("Login"):
            # Ensure the password matches your reference
            if username == "admin" and password == "xpds2026":
                st.session_state.authenticated = True
                st.success("Access Granted")
                st.rerun()
            else:
                st.error("Invalid credentials")