"""
Login Page
User authentication and login
"""

import streamlit as st
import logging
from utils.auth import verify_password, login_user, init_session_state

logger = logging.getLogger(__name__)


def show():
    """Display the Login page"""
    
    init_session_state()
    
    if st.session_state.get('authenticated', False):
        st.success(f"Already logged in as {st.session_state.user_name}")
        st.info("Use the sidebar to navigate to other pages")
        return
    
    st.markdown("<h1 style='color: #1f77b4;'>Login</h1>", unsafe_allow_html=True)
    st.markdown('<i class="fas fa-sign-in-alt"></i> Sign in to your account', unsafe_allow_html=True)
    
    db = st.session_state.db_client
    
    with st.form("login_form"):
        st.markdown("### Enter your credentials")
        
        email = st.text_input(
            "Email",
            placeholder="your.email@example.com",
            key="login_email"
        )
        
        password = st.text_input(
            "Password",
            type="password",
            placeholder="Enter your password",
            key="login_password"
        )
        
        submit_button = st.form_submit_button("Login", type="primary")

    if submit_button:
        if not email or not password:
            st.error("Please enter both email and password")
            return

        email = email.strip().lower()

        try:
            with st.spinner("Authenticating..."):
                user = db.get_user_by_email(email)

                if user and verify_password(password, user['password_hash']):
                    login_user(user['user_id'], user['name'], user['email'])
                    st.success(f"Welcome back, {user['name']}!")
                    logger.info(f"User logged in: {email}")
                    st.balloons()
                    st.rerun()
                else:
                    st.error("Invalid email or password")
                    logger.warning(f"Failed login: {email}")

        except Exception as e:
            st.error(f"Login error: {str(e)}")
            logger.error(f"Login error: {str(e)}", exc_info=True)
