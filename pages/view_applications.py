"""
View Applications Page
"""

import streamlit as st
import pandas as pd
from datetime import datetime
import logging
from utils.constants import VALID_STATUSES, JOB_TYPES, DEFAULT_COMPANY_LOGO

logger = logging.getLogger(__name__)


def format_date(date_str):
    """Convert date string to MM/DD/YY format"""
    if not isinstance(date_str, str):
        return date_str
    try:
        if 'T' in date_str or 'Z' in date_str:
            return datetime.fromisoformat(date_str.replace('Z', '+00:00')).strftime('%m/%d/%y')
        elif '-' in date_str and not date_str.startswith('0'):
            return datetime.strptime(date_str, '%Y-%m-%d').strftime('%m/%d/%y')
    except:
        pass
    return date_str


def render_timeline_stage(stage_name, is_active, date=None, is_first=False, is_last=False, next_is_active=False, is_rejected=False):
    """Render a single stage in the application timeline"""
    if is_rejected:
        circle_color = "#9e9e9e"
        line_color_left = "#9e9e9e"
        line_color_right = "#9e9e9e"
        shadow = '0 0 0 2px #e0e0e0'
    else:
        circle_color = "#00bcd4" if is_active else "#e0e0e0"
        line_color_left = "#00bcd4" if is_active else "#e0e0e0"
        line_color_right = "#00bcd4" if next_is_active else "#e0e0e0"
        shadow = '0 0 0 2px #e0f7fa' if is_active else 'none'
    
    left_line = f'<div style="flex: 1; height: 2px; background: {line_color_left}; align-self: center; {"visibility: hidden;" if is_first else ""}" ></div>'
    right_line = f'<div style="flex: 1; height: 2px; background: {line_color_right}; align-self: center; {"visibility: hidden;" if is_last else ""}" ></div>'
    
    html = '<div style="flex: 1; display: flex; flex-direction: column; align-items: center; justify-content: flex-start;">'
    html += f'<div style="font-size: 13px; color: #000; margin-bottom: 8px; font-weight: 600; white-space: nowrap; height: 15px;">{stage_name}</div>'
    html += '<div style="display: flex; align-items: center; width: 100%; height: 16px;">'
    html += left_line
    html += f'<div style="width: 16px; height: 16px; min-width: 16px; border-radius: 50%; background: {circle_color}; border: 3px solid #fff; box-shadow: {shadow}; flex-shrink: 0;"></div>'
    html += right_line
    html += '</div>'
    html += f'<div style="font-size: 12px; color: #555; margin-top: 6px; white-space: nowrap; height: 14px; font-weight: 600;">{date or ""}</div>'
    html += '</div>'
    return html


def get_stage_date(stage, current_status, status_dates):
    """Get the appropriate date for a timeline stage"""
    if stage == 'Saved':
        return status_dates.get('Saved', status_dates.get('Applied', ''))
    elif stage == 'Applied':
        return '' if current_status == 'Saved' else status_dates.get('Applied', '')
    else:
        return status_dates.get(stage, '')


def render_application_card(app, db):
    """Render a single application card with timeline"""
    try:
        job_data = app['jobs']
        company_data = job_data['companies']
        
        job_title = job_data['title']
        company_location = company_data.get('location', 'N/A')
        status = app['current_status']
        app_id = app['application_id']
        logo_url = company_data.get('logo_url', DEFAULT_COMPANY_LOGO)
        
        status_history = db.get_status_history(app_id)
        status_dates = {s['status']: s.get('status_date', '') for s in status_history}
        
        if status == 'Rejected':
            stages = VALID_STATUSES
            current_stage_idx = stages.index(status) if status in stages else 1
            is_rejected = True
        else:
            stages = [s for s in VALID_STATUSES if s != 'Rejected'] + ['_SPACER_']
            current_stage_idx = stages.index(status) if status in stages else 1
            is_rejected = False
        
        timeline_parts = ['<div style="display: flex; align-items: center; width: 100%; gap: 0;">']
        
        for idx, stage in enumerate(stages):
            if stage == '_SPACER_':
                timeline_parts.append('<div style="flex: 1; visibility: hidden;"></div>')
            else:
                stage_date = format_date(get_stage_date(stage, status, status_dates))
                is_last_visible = (idx == len(stages) - 1) or (idx < len(stages) - 1 and stages[idx + 1] == '_SPACER_')
                timeline_parts.append(render_timeline_stage(
                    stage, 
                    idx <= current_stage_idx,
                    stage_date,
                    idx == 0,
                    is_last_visible,
                    (idx + 1) <= current_stage_idx,
                    is_rejected
                ))
        
        timeline_parts.append('</div>')
        timeline_html = ''.join(timeline_parts)
        
        with st.container(border=True):
            col_logo, col_details, col_timeline, col_status, col_delete = st.columns([0.5, 1.5, 4, 1, 0.3])
        
        with col_logo:
            st.image(logo_url, width=48)
        
        with col_details:
            st.markdown(f"""
            <div style="margin-top: 4px; line-height: 1.4;">
                <div style="font-weight: 600; font-size: 18px; margin-bottom: 2px;">{job_title}</div>
                <div style="font-size: 14px; color: #555; margin-bottom: 2px;">{company_data['name']}</div>
                <div style="font-size: 13px; color: #777; margin-bottom: 8px;">{company_location}</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col_timeline:
            st.markdown(timeline_html, unsafe_allow_html=True)
        
        with col_status:
            st.markdown('<div style="margin-top: 4px;"></div>', unsafe_allow_html=True)
            current_index = VALID_STATUSES.index(status)
            
            selected = st.selectbox(
                f"status_label_{app_id}",
                options=VALID_STATUSES,
                index=current_index,
                key=f"status_{app_id}",
                label_visibility="collapsed"
            )
            
            if selected != status:
                from datetime import date
                if db.update_application_status(app_id, selected, date.today(), None):
                    st.success(f"Updated to {selected}")
                    st.rerun()
        
            with col_delete:
                st.markdown('<div style="margin-top: 4px;"></div>', unsafe_allow_html=True)
                if st.button("", icon=":material/delete:", type="primary", key=f"delete_{app_id}", help="Delete this application", width="stretch"):
                    st.session_state[f"show_delete_dialog_{app_id}"] = True
                    st.rerun()
    
    except Exception as e:
        logger.error(f"Error rendering card: {str(e)}")


def show():
    """Display the View Applications page"""
    
    st.markdown("<h1 style='color: #1f77b4;'>Your Job Tracker</h1>", unsafe_allow_html=True)
    
    db = st.session_state.db_client
    
    @st.dialog("Confirm Delete")
    def delete_confirmation(app_id):
        st.write("Are you sure you want to delete this application?")
        st.write("This action cannot be undone.")
        st.write("")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Yes, Delete", type="primary", width="stretch", key=f"dialog_yes_{app_id}"):
                if db.delete_application(app_id):
                    del st.session_state[f"show_delete_dialog_{app_id}"]
                    st.rerun()
        with col2:
            if st.button("Cancel", width="stretch", key=f"dialog_no_{app_id}"):
                del st.session_state[f"show_delete_dialog_{app_id}"]
                st.rerun()
    
    try:
        user_id = st.session_state.get('user_id')
        all_applications = db.get_all_applications(user_id, None)
        
        if not all_applications:
            st.info("No applications found. Add your first application!")
            return
        
        total_count = len(all_applications)
        
        st.markdown(f"### {total_count} Total Jobs")
        
        col1, col2, col3, col4 = st.columns([3, 2, 2, 2])
        
        with col1:
            search_term = st.text_input(
                "Search",
                placeholder="Search for roles or companies",
                label_visibility="collapsed"
            )
        
        with col2:
            job_type_filter = st.multiselect(
                "Job Type",
                JOB_TYPES,
                default=[],
                placeholder="All Types",
                label_visibility="collapsed"
            )
        
        with col3:
            status_filter = st.multiselect(
                "Status",
                VALID_STATUSES,
                default=[],
                placeholder="All Statuses",
                label_visibility="collapsed"
            )
        
        with col4:
            export_data = [{
                'Company': a['jobs']['companies']['name'],
                'Title': a['jobs']['title'],
                'Status': a['current_status'],
                'Status Date': a['status_changed_date']
            } for a in all_applications]
            
            csv = pd.DataFrame(export_data).to_csv(index=False)
            
            st.download_button(
                "Export CSV",
                csv,
                f"jobs_{datetime.now().strftime('%Y%m%d')}.csv",
                width="stretch"
            )
        
        st.markdown("---")
        
        filtered_apps = all_applications
        
        if search_term:
            filtered_apps = [
                a for a in filtered_apps
                if search_term.lower() in a['jobs']['companies']['name'].lower()
                or search_term.lower() in a['jobs']['title'].lower()
            ]
        
        if status_filter:
            filtered_apps = [a for a in filtered_apps if a['current_status'] in status_filter]
        
        if job_type_filter:
            filtered_apps = [a for a in filtered_apps if a['jobs'].get('job_type') in job_type_filter]
        
        st.caption(f"Showing {len(filtered_apps)} applications")
        
        for app in filtered_apps:
            render_application_card(app, db)
            app_id = app['application_id']
            if st.session_state.get(f"show_delete_dialog_{app_id}", False):
                delete_confirmation(app_id)
        
        logger.info(f"Displayed {len(filtered_apps)} applications")
        
    except Exception as e:
        st.error(f"Error loading applications: {str(e)}")
        logger.error(f"Error in view_applications: {str(e)}", exc_info=True)