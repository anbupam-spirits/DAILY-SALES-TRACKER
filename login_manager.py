import streamlit as st
from database import authenticate_user

def init_auth_session():
    """Initializes auth keys in session state."""
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    if 'user' not in st.session_state:
        st.session_state.user = None

def login(username, password):
    """Logs in a user."""
    user = authenticate_user(username, password)
    if user:
        st.session_state.logged_in = True
        st.session_state.user = {
            "id": user.id,
            "username": user.username,
            "role": user.role,
            "full_name": user.full_name
        }
        return True
    return False

def logout():
    """Logs out a user."""
    st.session_state.logged_in = False
    st.session_state.user = None
    st.rerun()

def login_form():
    """Renders a simple login form."""
    st.title("🔐 Login")
    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Login")
        
        if submitted:
            if login(username, password):
                st.success("Logged in successfully!")
                st.rerun()
            else:
                st.error("Invalid username or password")

def require_auth():
    """Higher-order logic to check if user is logged in."""
    init_auth_session()
    if not st.session_state.logged_in:
        login_form()
        st.stop()
