import streamlit as st

def login_page():
    """
    Standard Authentication Layer for TIP Projects.
    """
    st.markdown("""
        <style>
            .login-box {
                background-color: #1e1e1e;
                padding: 2rem;
                border-radius: 10px;
                border: 1px solid #333;
            }
        </style>
    """, unsafe_content_allowed=True)

    with st.container():
        st.title("🔒 XPDS Secure Access")
        st.info("Please enter your credentials to access the Diagnostic Engine.")
        
        # Simple authentication logic
        user = st.text_input("Username")
        password = st.text_input("Password", type="password")
        
        if st.button("Login"):
            # Replace 'admin' / 'xpds2026' with your preferred credentials
            if user == "admin" and password == "xpds2026":
                st.session_state.authenticated = True
                st.success("Access Granted. Redirecting...")
                st.rerun()
            else:
                st.error("Invalid credentials. Please try again.")

def check_auth():
    """
    Utility function to ensure a user hasn't bypassed the landing page.
    """
    if 'authenticated' not in st.session_state or not st.session_state.authenticated:
        st.warning("Please log in to continue.")
        st.stop()
