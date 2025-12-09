"""
Dashboard Page
Overview and analytics with comprehensive metrics and Sankey visualization
"""

import streamlit as st
from datetime import datetime
import logging
import pandas as pd
import plotly.graph_objects as go

logger = logging.getLogger(__name__)


def show():
    """Display the Dashboard page"""
    
    st.markdown("<h1 style='color: #1f77b4;'>Dashboard</h1>", unsafe_allow_html=True)
    
    db = st.session_state.db_client
    user_id = st.session_state.get('user_id')
    
    try:
        applications = db.get_all_applications(user_id)
        
        status_history_map = {}
        for app in applications:
            status_history_map[app['application_id']] = db.get_status_history(app['application_id'])
        
        stats = db.get_application_stats(user_id, applications)
        applied_apps = [a for a in applications if a.get('current_status') != 'Saved']
        
        ghosted_count = sum(1 for a in applied_apps if a.get('current_status') in ['Applied', 'Interview'])
        total_applied_apps = len(applied_apps)
        ghost_rate = round((ghosted_count / total_applied_apps * 100), 1) if total_applied_apps > 0 else 0.0
        
        perf_metrics = db.get_performance_metrics(user_id, applied_apps, status_history_map)
        volume_metrics = db.get_volume_metrics(user_id, applied_apps)
        conversion = db.get_conversion_funnel(user_id, applied_apps)
        sankey_data = db.get_sankey_data(user_id, applied_apps, status_history_map)

        css = """
        <style>
        .st-key-grey-bg {
            background-color: #f8f9fa;
            padding: 20px;
            border-radius: 10px;
        }
        .st-key-white1-bg {
            background-color: #ffffff;
        }
        .st-key-white2-bg {
            background-color: #ffffff;
        }
        .st-key-white3-bg {
            background-color: #ffffff;
        }
        .st-key-white4-bg {
            background-color: #ffffff;
        }
        </style>
        """
        st.html(css)

        with st.container(border=True, height="stretch"):
            total_excluding_saved = sum(count for status, count in stats['by_status'].items() if status != 'Saved')
            st.markdown(f"<h3 style='margin:0; padding:16px; font-size:1.5rem; font-weight:700; color:#1a1a1a;'>{total_excluding_saved} Applications</h3>", unsafe_allow_html=True)
            
            with st.container(border=True, key="grey-bg", height="stretch"):
                st.markdown("<h4 style='margin:0; padding:12px 16px; font-size:1.5rem; font-weight:700; color:#1a1a1a; background-color:#f8f9fa; border-radius:8px;'>Insights</h4>", unsafe_allow_html=True)
                st.markdown("<div style='height:12px;'></div>", unsafe_allow_html=True)
                
                metric_col1, metric_col2, metric_col3 = st.columns([0.3, 0.4, 0.3], gap="small")
                
                with metric_col1:
                    with st.container(border=True, key="white1-bg", height="stretch"):
                        st.markdown("<p style='margin:0; padding:8px 12px; font-size:0.95rem; font-weight:700; color:#1a1a1a;'>Performance Metrics</p>", unsafe_allow_html=True)
                        st.markdown("<div style='height:8px;'></div>", unsafe_allow_html=True)
                        
                        st.markdown(f"""
                        <div style='padding:12px; background-color:#fff9f5; border-radius:8px; margin-bottom:8px;'>
                            <p style='margin:0; font-size:0.85rem; color:#666; font-weight:500;'>Ghost Rate</p>
                            <p style='margin:4px 0 0 0; font-size:1.8rem; font-weight:700; color:#ff6b35;'>{ghost_rate}%</p>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        st.markdown(f"""
                        <div style='padding:12px; background-color:#f8f9fa; border-radius:8px; margin-bottom:8px;'>
                            <p style='margin:0; font-size:0.85rem; color:#666; font-weight:500;'>Response Time</p>
                            <p style='margin:4px 0 0 0; font-size:1.8rem; font-weight:700; color:#2c3e50;'>{perf_metrics['response_time']} days</p>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        st.markdown(f"""
                        <div style='padding:12px; background-color:#f8f9fa; border-radius:8px; margin-bottom:12px;'>
                            <p style='margin:0; font-size:0.85rem; color:#666; font-weight:500;'>Longest Waiting Application</p>
                            <p style='margin:4px 0 0 0; font-size:1.8rem; font-weight:700; color:#2c3e50;'>{perf_metrics['longest_waiting']} days</p>
                        </div>
                        """, unsafe_allow_html=True)
                
                with metric_col2:
                    with st.container(border=True, key="white2-bg", height="stretch"):
                        st.markdown("<p style='margin:0; padding:8px 12px; font-size:0.95rem; font-weight:700; color:#1a1a1a;'>Volume Metrics</p>", unsafe_allow_html=True)
                        st.markdown("<div style='height:8px;'></div>", unsafe_allow_html=True)
                        
                        st.markdown(f"""
                        <div style='padding:12px; background-color:#f0fdf4; border-radius:8px; margin-bottom:8px;'>
                            <p style='margin:0; font-size:0.85rem; color:#666; font-weight:500;'>Total Applications</p>
                            <p style='margin:4px 0 0 0; font-size:1.8rem; font-weight:700; color:#16a34a;'>{volume_metrics['total_applications']}</p>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        st.markdown(f"""
                        <div style='padding:12px; background-color:#f8f9fa; border-radius:8px; margin-bottom:8px;'>
                            <p style='margin:0; font-size:0.85rem; color:#666; font-weight:500;'>Most Active Day</p>
                            <div style='display:flex; align-items:baseline; gap:8px; margin-top:4px;'>
                                <p style='margin:0; font-size:1.8rem; font-weight:700; color:#2c3e50;'>{volume_metrics['most_active_day']}</p>
                                <span style='display:inline-block; padding:4px 10px; background-color:#e5e7eb; border-radius:12px; font-size:0.75rem; color:#666; font-weight:600;'>{volume_metrics['most_active_count']} apps</span>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        with st.container(border=True, key="white3-bg", height="stretch"):
                            st.markdown("<p style='margin:0; padding:6px; font-size:0.85rem; font-weight:600; color:#1a1a1a; background-color:#f8f9fa; border-radius:6px;'>Application Rate</p>", unsafe_allow_html=True)
                            st.markdown("<div style='height:4px;'></div>", unsafe_allow_html=True)
                            
                            st.markdown(f"""
                            <div style='display:flex; gap:8px; justify-content:space-between; padding-bottom:6px;'>
                                <div style='flex:1; padding:8px 4px; background-color:#f8f9fa; border-radius:6px; text-align:center;'>
                                    <p style='margin:0 0 4px 0; font-size:1.4rem; font-weight:700; color:#2c3e50;'>{volume_metrics['rate_per_day']}</p>
                                    <span style='display:inline-block; padding:2px 8px; background-color:#e5e7eb; border-radius:12px; font-size:0.75rem; color:#666; font-weight:600;'>/day</span>                  
                                </div>
                                <div style='flex:1; padding:8px 4px; background-color:#f8f9fa; border-radius:6px; text-align:center;'>
                                    <p style='margin:0 0 4px 0; font-size:1.4rem; font-weight:700; color:#2c3e50;'>{volume_metrics['rate_per_week']}</p>
                                    <span style='display:inline-block; padding:2px 8px; background-color:#e5e7eb; border-radius:12px; font-size:0.75rem; color:#666; font-weight:600;'>/wk</span>
                                </div>
                                <div style='flex:1; padding:8px 4px; background-color:#f8f9fa; border-radius:6px; text-align:center;'>
                                    <p style='margin:0 0 4px 0; font-size:1.4rem; font-weight:700; color:#2c3e50;'>{volume_metrics['rate_per_month']}</p>
                                    <span style='display:inline-block; padding:2px 8px; background-color:#e5e7eb; border-radius:12px; font-size:0.75rem; color:#666; font-weight:600;'>/mo</span>
                                </div>
                                <div style='flex:1; padding:8px 4px; background-color:#f8f9fa; border-radius:6px; text-align:center;'>
                                    <p style='margin:0 0 4px 0; font-size:1.4rem; font-weight:700; color:#2c3e50;'>{volume_metrics['rate_per_year']}</p>
                                    <span style='display:inline-block; padding:2px 8px; background-color:#e5e7eb; border-radius:12px; font-size:0.75rem; color:#666; font-weight:600;'>/yr</span>
                                </div>
                            </div>
                            """, unsafe_allow_html=True)
                
                with metric_col3:
                    with st.container(border=True, key="white4-bg", height="stretch"):
                        st.markdown("<p style='margin:0; padding:8px 12px; font-size:0.95rem; font-weight:700; color:#1a1a1a;'>Conversion Funnel</p>", unsafe_allow_html=True)
                        st.markdown("<div style='height:8px;'></div>", unsafe_allow_html=True)
                        
                        st.markdown(f"""
                        <div style='padding:12px; background-color:#fef2f2; border-radius:8px; margin-bottom:8px;'>
                            <p style='margin:0; font-size:0.85rem; color:#666; font-weight:500;'>Applied → Interview</p>
                            <p style='margin:4px 0 0 0; font-size:1.8rem; font-weight:700; color:#dc2626;'>{conversion['applied_to_interview']}%</p>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        st.markdown(f"""
                        <div style='padding:12px; background-color:#f8f9fa; border-radius:8px; margin-bottom:12px;'>
                            <p style='margin:0; font-size:0.85rem; color:#666; font-weight:500;'>Interview → Offer</p>
                            <p style='margin:4px 0 0 0; font-size:1.8rem; font-weight:700; color:#2c3e50;'>{conversion['interview_to_offer']}%</p>
                        </div>
                        """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        st.markdown("### Application Flow")
        
        if sankey_data['sources'] and sankey_data['targets'] and sankey_data['values']:
            # Node colors: Applied, Rejected, Ghosted, Offer, Interviewing
            NODE_COLORS = ["#5B8DEE", "#FF6B6B", "#B8A1D6", "#7CB342", "#4DB6AC"]
            # Node positions: x=[left, right, right, right, middle], y=[middle, top, middle, bottom, middle]
            NODE_X = [0.001, 0.999, 0.999, 0.999, 0.35]
            NODE_Y = [0.5, 0.15, 0.5, 0.85, 0.5]
            
            fig = go.Figure(data=[go.Sankey(
                textfont=dict(color="black", size=12),
                node=dict(
                    pad=80,
                    thickness=15,
                    line=dict(color="white", width=2.5),
                    label=sankey_data['labels'],
                    color=NODE_COLORS,
                    x=NODE_X,
                    y=NODE_Y,
                    hovertemplate='%{label}<extra></extra>'
                ),
                link=dict(
                    source=sankey_data['sources'],
                    target=sankey_data['targets'],
                    value=sankey_data['values'],
                    color=sankey_data['colors'],
                    hovertemplate='%{value} applications<extra></extra>'
                )
            )])
            
            fig.update_layout(
                font=dict(size=12, color='black', family='Arial'),
                height=500,
                plot_bgcolor='white',
                paper_bgcolor='white',
                margin=dict(l=150, r=200, t=20, b=20),
                hovermode='closest'
            )
            
            st.plotly_chart(fig, width='stretch')
        else:
            st.info("No application data to display in flow diagram yet. Start applying to see your funnel!")
        
        st.markdown("---")
        
        st.markdown("### Status Breakdown")
        
        if stats['total'] > 0:
            sankey_counts = sankey_data['counts']
            
            status_data = [
                {'Status': 'Saved', 'Applications': stats['by_status'].get('Saved', 0)},
                {'Status': 'Applied', 'Applications': sankey_counts['applied']},
                {'Status': 'Interviewing', 'Applications': sankey_counts['interviewing']},
                {'Status': 'Offer', 'Applications': sankey_counts['offer']},
                {'Status': 'Rejected', 'Applications': sankey_counts['rejected']},
                {'Status': 'Ghosted', 'Applications': sankey_counts['ghosted']}
            ]
            
            status_df = pd.DataFrame(status_data)
            
            st.dataframe(
                status_df,
                width='stretch',
                hide_index=True,
                column_config={
                    "Status": st.column_config.TextColumn(
                        "Status",
                        width="medium",
                    ),
                    "Applications": st.column_config.NumberColumn(
                        "Applications",
                        format="%d",
                        width="small",
                    ),
                }
            )
        else:
            st.info("No applications yet. Start tracking to see status breakdown!")
        
        st.markdown("---")
        
        st.markdown("### Recent Activity")
        
        if applications:
            recent_apps = applications[:10]
            
            status_colors = {
                'Saved': 'background-color: #e3f2fd; color: #1976d2;',
                'Applied': 'background-color: #fff3e0; color: #f57c00;',
                'Interview': 'background-color: #f3e5f5; color: #7b1fa2;',
                'Offer': 'background-color: #e8f5e9; color: #388e3c;',
                'Rejected': 'background-color: #ffebee; color: #d32f2f;'
            }
            
            for app in recent_apps:
                try:
                    company = app['jobs']['companies']['name']
                    title = app['jobs']['title']
                    status = app['current_status']
                    status_changed_dt = datetime.fromisoformat(
                        app['status_changed_date'].replace('Z', '+00:00')
                    )
                    status_changed_date = status_changed_dt.strftime('%m/%d/%y')
                    
                    status_display = status
                    if status in ['Applied', 'Interview']:
                        days_since = (datetime.now(status_changed_dt.tzinfo) - status_changed_dt).days
                        status_display = f"{status} (Ghosted {days_since}d)"
                    
                    color_style = status_colors.get(status, 'background-color: #f5f5f5; color: #666;')
                    
                    st.markdown(
                        f"**{title}** at _{company}_ - "
                        f"<span style='{color_style} padding: 3px 8px; border-radius: 4px; font-size: 0.85em; font-weight: 600;'>{status_display}</span> "
                        f"<span style='color: #999; font-size: 0.85em;'>({status_changed_date})</span>",
                        unsafe_allow_html=True
                    )
                except Exception as e:
                    logger.error(f"Error displaying application: {str(e)}")
                    continue
        else:
            st.info("No applications yet")
        
        st.markdown("---")
        
        # Insights & Tips
        st.markdown("### Insights & Tips")
        
        insights = []
        
        if stats['total'] == 0:
            insights.append("Start tracking your applications to see insights!")
        else:
            if ghost_rate > 50:
                insights.append(
                    f"Your ghost rate is {ghost_rate}%. "
                    "Consider following up on pending applications or focusing on more responsive companies."
                )
            
            if volume_metrics['rate_per_week'] < 5:
                insights.append(
                    "Consider increasing your application volume. "
                    "More applications = more opportunities!"
                )
            
            interview_count = stats['by_status'].get('Interview', 0)
            if interview_count > 0:
                insights.append(
                    f"Great! You have {interview_count} interview(s). "
                    "Prepare well and showcase your skills!"
                )
            
            offer_count = stats['by_status'].get('Offer', 0)
            if offer_count > 0:
                insights.append(
                    f"Congratulations! You have {offer_count} offer(s). "
                    "Take time to evaluate and negotiate!"
                )
        
        for insight in insights:
            st.info(insight)
        
        logger.info("Dashboard displayed successfully")
        
    except Exception as e:
        st.error(f"Error loading dashboard: {str(e)}")
        logger.error(f"Error in dashboard: {str(e)}", exc_info=True)
