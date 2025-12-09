"""
Job Application Tracker
A Streamlit app for tracking job applications with Supabase backend
"""

import streamlit as st
from pages import add_application, view_applications, dashboard, login, signup
from utils.database import SupabaseClient
from utils.logger_config import setup_logger
from utils.auth import init_session_state, is_authenticated, logout_user

logger = setup_logger()

st.set_page_config(
    page_title="Job Application Tracker",
    page_icon=":briefcase:",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        [data-testid="stSidebarNav"] {
            display: none;
        }
        
        .stButton>button {
            width: 100%;
        }
        
        h1 {
            color: #1f77b4;
        }
        
        .status-saved {
            background-color: #e3f2fd;
            padding: 0.2rem 0.5rem;
            border-radius: 0.3rem;
        }
        
        .status-applied {
            background-color: #fff3e0;
            padding: 0.2rem 0.5rem;
            border-radius: 0.3rem;
        }
        
        .status-interview {
            background-color: #f3e5f5;
            padding: 0.2rem 0.5rem;
            border-radius: 0.3rem;
        }
        
        .status-offer {
            background-color: #e8f5e9;
            padding: 0.2rem 0.5rem;
            border-radius: 0.3rem;
        }
        
        .status-rejected {
            background-color: #ffebee;
            padding: 0.2rem 0.5rem;
            border-radius: 0.3rem;
        }
        
        .info-box {
            background-color: #e7f3ff;
            border-left: 4px solid #2196F3;
            padding: 12px;
            margin: 8px 0;
            border-radius: 4px;
        }
        
        .fas, .far, .fab {
            margin-right: 8px;
        }
    </style>
""", unsafe_allow_html=True)

def main():
    if 'db_client' not in st.session_state:
        try:
            st.session_state.db_client = SupabaseClient()
            logger.info("Database client initialized")
        except Exception as e:
            st.error(f"Failed to initialize database connection: {str(e)}")
            logger.error(f"Database initialization error: {str(e)}")
            st.stop()
    
    init_session_state()
    
    if 'page' not in st.session_state:
        st.session_state.page = "Login"
    
    authenticated = is_authenticated()
    
    st.sidebar.title("Navigation")
    st.sidebar.markdown("---")

    if not authenticated:    
        st.session_state.page = st.sidebar.radio(
            "Select Page",
            ["Login", "Signup"],
            index= 0 if st.session_state.page == "Login" else 1,
            key="page_selector"
        )

        page = st.session_state.page
        st.sidebar.markdown("---")
        st.sidebar.info("Please login or signup to access the application")
    else:
        st.sidebar.markdown(
            f"<div style='background-color: #e8f5e9; border-left: 4px solid #4caf50; padding: 12px; border-radius: 4px;'>"
            f"<i class='fas fa-user-circle'></i> <strong>Logged in:</strong><br/>{st.session_state.user_name}<br/>"
            f"<small>{st.session_state.user_email}</small></div>",
            unsafe_allow_html=True
        )
        st.sidebar.markdown("---")
        
        page = st.sidebar.radio(
            "Select Page",
            ["Dashboard", "Add Application", "View Applications"],
            index=0
        )
        
        st.sidebar.markdown("---")
        st.sidebar.markdown(
            '<div style="background-color: #e7f3ff; border-left: 4px solid #2196F3; padding: 12px; border-radius: 4px;">'
            '<i class="fas fa-info-circle"></i> <strong>Tip:</strong> Applications with \'Applied\' status show ghosted days from application date until rejected or status changed'
            '</div>', 
            unsafe_allow_html=True
        )
        
        st.sidebar.markdown("---")
        if st.sidebar.button("Logout", width="stretch"):
            logout_user()
            st.session_state.page = "Login"
            st.rerun()
    
    if page == "Login":
        login.show()
    elif page == "Signup":
        signup.show()
    elif page == "Dashboard":
        dashboard.show()
    elif page == "Add Application":
        add_application.show()
    elif page == "View Applications":
        view_applications.show()

if __name__ == "__main__":
    main()
