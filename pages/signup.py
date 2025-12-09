"""
Signup Page
User registration
"""

import streamlit as st
import logging
from utils.auth import hash_password, login_user, init_session_state

logger = logging.getLogger(__name__)


def show():
    """Display the Signup page"""
    
    init_session_state()
    
    if st.session_state.get('authenticated', False):
        st.success(f"Already logged in as {st.session_state.user_name}")
        st.info("Use the sidebar to navigate to other pages")
        return
    
    st.markdown("<h1 style='color: #1f77b4;'>Sign Up</h1>", unsafe_allow_html=True)
    st.markdown('<i class="fas fa-user-plus"></i> Create a new account', unsafe_allow_html=True)
    
    db = st.session_state.db_client
    
    with st.form("signup_form"):
        st.markdown("### Enter your information")
        
        name = st.text_input(
            "Full Name",
            placeholder="John Doe",
            key="signup_name"
        )
        
        email = st.text_input(
            "Email",
            placeholder="your.email@example.com",
            key="signup_email"
        )
        
        password = st.text_input(
            "Password",
            type="password",
            placeholder="Enter password",
            key="signup_password"
        )
        
        confirm_password = st.text_input(
            "Confirm Password",
            type="password",
            placeholder="Re-enter password",
            key="signup_confirm_password"
        )
        
        submit_button = st.form_submit_button("Sign Up", type="primary")

    if submit_button:
        errors = []
        
        if not name or not name.strip():
            errors.append("Name is required")
        
        if not email or not email.strip():
            errors.append("Email is required")
        elif '@' not in email or '.' not in email:
            errors.append("Invalid email format")
        
        if not password:
            errors.append("Password is required")
        
        if password != confirm_password:
            errors.append("Passwords do not match")
        
        if errors:
            for error in errors:
                st.error(error)
            return
        
        name = name.strip()
        email = email.strip().lower()
        
        try:
            with st.spinner("Creating account..."):
                if db.get_user_by_email(email):
                    st.error("Email already exists. Please login instead.")
                    logger.warning(f"Duplicate email: {email}")
                    return
                
                password_hash = hash_password(password)
                user_id = db.create_user_with_password(name, email, password_hash)
                
                if user_id:
                    st.success(f"Account created! Welcome, {name}!")
                    logger.info(f"New user: {email}")
                    login_user(user_id, name, email)
                    st.balloons()
                    st.rerun()
                else:
                    st.error("Failed to create account. Try again.")
                    logger.error("User creation failed")
                    
        except Exception as e:
            st.error(f"Signup error: {str(e)}")
            logger.error(f"Signup error: {str(e)}", exc_info=True)
    
    st.markdown("---")
    st.info("Already have an account? Use the **Login** page")
