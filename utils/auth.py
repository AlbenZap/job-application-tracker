"""
Authentication utilities for user login and session management
"""

import streamlit as st
import bcrypt
import logging

logger = logging.getLogger(__name__)


def hash_password(password: str) -> str:
    """Hash password using bcrypt"""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')


def verify_password(password: str, hashed_password: str) -> bool:
    """Verify password against hashed password using bcrypt"""
    try:
        return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))
    except Exception as e:
        logger.error(f"Password verification error: {str(e)}")
        return False


def init_session_state():
    """Initialize authentication session state variables"""
    st.session_state.setdefault('authenticated', False)
    st.session_state.setdefault('user_id', None)
    st.session_state.setdefault('user_name', None)
    st.session_state.setdefault('user_email', None)


def login_user(user_id: int, name: str, email: str):
    """Set session state for logged-in user"""
    st.session_state.authenticated = True
    st.session_state.user_id = user_id
    st.session_state.user_name = name
    st.session_state.user_email = email
    logger.info(f"User logged in: {email}")


def logout_user():
    """Clear session state to log out user"""
    st.session_state.authenticated = False
    st.session_state.user_id = None
    st.session_state.user_name = None
    st.session_state.user_email = None
    logger.info("User logged out")


def is_authenticated() -> bool:
    """Check if user is authenticated"""
    return st.session_state.get('authenticated', False)
