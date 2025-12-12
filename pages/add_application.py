"""
Add Application Page
Form to create new job applications
"""

import streamlit as st
from datetime import datetime, date
import logging
from streamlit_searchbox import st_searchbox
from utils.constants import JOB_TYPES, DEFAULT_COMPANY_LOGO
from utils.company_api import search_companies

logger = logging.getLogger(__name__)


def search_company_autocomplete(search_term):
    """Search and return company names for autocomplete dropdown"""
    if not search_term or len(search_term) < 2:
        return []
    
    companies = search_companies(search_term)
    return [company.get('name', 'Unknown') for company in companies[:10]]


def show():
    """Display the Add Application page"""
    
    st.markdown("<h1 style='color: #1f77b4;'>Add New Application</h1>", unsafe_allow_html=True)
    st.markdown("Fill in the details below to track a new job application.")
    
    db = st.session_state.db_client

    st.session_state.selected_company_name = ''
    st.session_state.selected_company_logo = ''
    st.session_state.selected_company_industry = ''
    st.session_state.selected_company_location = ''
    
    st.markdown("### <i class='fas fa-search'></i> Search Company", unsafe_allow_html=True)
    
    selected_company_name = st_searchbox(
        search_company_autocomplete,
        placeholder="Start typing company name (e.g., Apple, Google)...",
        key="company_searchbox"
    )
    
    if selected_company_name:
        companies = search_companies(selected_company_name)
        if companies:
            selected_company = next(
                (c for c in companies if c.get('name') == selected_company_name),
                companies[0]
            )
            
            col_logo, col_info = st.columns([1, 5])
            with col_logo:
                if selected_company.get('logo'):
                    st.image(selected_company['logo'], width=60)
            with col_info:
                st.markdown(
                    f"<div style='background-color: #d4edda; border-left: 4px solid #28a745; padding: 12px; border-radius: 4px; color: #155724;'>"
                    f"<i class='fas fa-check-circle'></i> <strong>Selected:</strong> {selected_company['name']}"
                    f"</div>",
                    unsafe_allow_html=True
                )
            
            st.session_state.selected_company_name = selected_company.get('name', '')
            st.session_state.selected_company_logo = selected_company.get('logo', '')
            st.session_state.selected_company_industry = selected_company.get('industry', '')
            st.session_state.selected_company_location = selected_company.get('location', '')
        else:
            st.session_state.selected_company_name = selected_company_name
            st.session_state.selected_company_logo = ''
            st.session_state.selected_company_industry = ''
            st.session_state.selected_company_location = ''
    
    st.markdown("---")
    
    with st.form("add_application_form", clear_on_submit=True):
        st.subheader("Company & Job Details")
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("Company Name <span style='color:red'>*</span>", unsafe_allow_html=True)
            company_name = st.text_input(
                "Company Name", 
                value=st.session_state.selected_company_name,
                placeholder="Company Name",
                label_visibility="collapsed"
            )
        with col2:
            st.markdown("Industry&nbsp;", unsafe_allow_html=True)
            company_industry = st.text_input(
                "Industry", 
                value=st.session_state.selected_company_industry,
                placeholder="e.g., Technology, Finance",
                label_visibility="collapsed"
            )
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("Company Location&nbsp;", unsafe_allow_html=True)
            company_location = st.text_input(
                "Company Location", 
                value=st.session_state.selected_company_location,
                placeholder="San Francisco, CA", 
                label_visibility="collapsed"
            )
        with col2:
            st.markdown("Job Location&nbsp;", unsafe_allow_html=True)
            job_location = st.text_input("Job Location", placeholder="Remote / On-site", label_visibility="collapsed")
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("Job Title <span style='color:red'>*</span>", unsafe_allow_html=True)
            job_title = st.text_input("Job Title *", placeholder="Software Engineer", label_visibility="collapsed")
        with col2:
            st.markdown("Job Type&nbsp;", unsafe_allow_html=True)
            job_type = st.selectbox("Job Type", [""] + JOB_TYPES, label_visibility="collapsed")
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("Job Posted Date (Optional)&nbsp;", unsafe_allow_html=True)
            posted_date = st.date_input(
                "Job Posted Date (Optional)",
                value=None,
                max_value=date.today(),
                label_visibility="collapsed"
            )
        with col2:
            st.markdown("Date <span style='color:red'>*</span>", unsafe_allow_html=True)
            status_date = st.date_input(
                "Date *",
                value=date.today(),
                max_value=date.today(),
                label_visibility="collapsed"
            )
        
        st.markdown("---")        
        notes = st.text_area(
            "Notes",
            placeholder="Add any relevant notes about this application...",
            height=100
        )
        
        st.markdown("---")
        
        col1, col2, col3 = st.columns([1, 1, 2])
        with col1:
            save_button = st.form_submit_button("Save Application", width="stretch", type="secondary")
        with col2:
            submit_button = st.form_submit_button("Add Application", width="stretch", type="primary")
    
    if submit_button or save_button:
        user_id = st.session_state.get('user_id')
        
        current_status = "Applied" if submit_button else "Saved"
        
        errors = []
        if not company_name or not company_name.strip():
            errors.append("Company name is required")
        if not job_title or not job_title.strip():
            errors.append("Job title is required")
        if posted_date and status_date and posted_date > status_date:
            errors.append("Job posted date cannot be after the application date")
        
        if errors:
            for error in errors:
                st.error(error)
            logger.warning(f"Form validation failed: {errors}")
        else:
            try:
                with st.spinner("Saving application..."):
                    if not user_id:
                        st.error("User session invalid. Please login again.")
                        return
                    
                    company_id = db.get_or_create_company(
                        company_name.strip(),
                        company_industry.strip() if company_industry else None,
                        company_location.strip() if company_location else None,
                        st.session_state.selected_company_logo or DEFAULT_COMPANY_LOGO
                    )
                    if not company_id:
                        st.error("Failed to create/retrieve company")
                        return
                    
                    job_id = db.get_or_create_job(
                        company_id,
                        job_title.strip(),
                        job_type if job_type else None,
                        job_location.strip() if job_location else None,
                        posted_date
                    )
                    if not job_id:
                        st.error("Failed to create/retrieve job")
                        return
                    
                    success = db.create_application(
                        job_id,
                        user_id,
                        status_date,
                        current_status,
                        notes.strip() if notes else None
                    )
                    
                    if success:
                        action = "saved" if save_button else "added"
                        icon = ":material/save:" if save_button else ":material/check_circle:"
                        st.toast(f"Application {action} successfully!", icon=icon)
                        logger.info(f"Application created: {company_name} - {job_title} ({current_status})")
                        
                        st.success(f":material/task_alt: **{current_status}:** {job_title} at {company_name}")
                    else:
                        st.error("Failed to create application")
                        logger.error("Application creation failed")
                        
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")
                logger.error(f"Error adding application: {str(e)}", exc_info=True)
    
    st.markdown("---")
    st.markdown("### Recent Applications")
    
    user_id = st.session_state.get('user_id')
    try:
        all_apps = db.get_all_applications(user_id)
        recent_apps = all_apps[:5] if all_apps else []
        
        if recent_apps:
            for app in recent_apps:
                company = app['jobs']['companies']['name']
                title = app['jobs']['title']
                status = app['current_status']
                status_changed = datetime.fromisoformat(app['status_changed_date'].replace('Z', '+00:00')).strftime('%m/%d/%y')
                               
                status_colors = {
                    'Saved': 'background-color: #e3f2fd; color: #1976d2;',
                    'Applied': 'background-color: #fff3e0; color: #f57c00;',
                    'Interview': 'background-color: #f3e5f5; color: #7b1fa2;',
                    'Offer': 'background-color: #e8f5e9; color: #388e3c;',
                    'Rejected': 'background-color: #ffebee; color: #d32f2f;'
                }
                
                color_style = status_colors.get(status, 'background-color: #f5f5f5; color: #666;')
                
                st.markdown(
                    f"**{title}** at _{company}_ - "
                    f"<span style='{color_style} padding: 3px 8px; border-radius: 4px; font-size: 0.85em; font-weight: 600;'>{status}</span> "
                    f"<span style='color: #999; font-size: 0.85em;'>({status_changed})</span>",
                    unsafe_allow_html=True
                )
        else:
            st.info("No applications yet. Add your first one above!")
    except Exception as e:
        st.warning("Could not load recent applications")
        logger.error(f"Error loading recent applications: {str(e)}")
