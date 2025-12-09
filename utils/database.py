""" 
Database client for Supabase integration
Handles all CRUD operations and business logic
"""

import streamlit as st
from supabase import create_client, Client
from datetime import datetime
import logging
from typing import List, Dict, Optional
from .constants import VALID_STATUSES

logger = logging.getLogger(__name__)


class SupabaseClient:
    """Supabase database operations wrapper"""
    
    def __init__(self):
        try:
            url = st.secrets["supabase"]["url"]
            key = st.secrets["supabase"]["key"]
            self.client: Client = create_client(url, key)
            logger.info("Supabase client initialized")
        except Exception as e:
            logger.error(f"Failed to initialize Supabase client: {str(e)}")
            raise
    
    
    def create_user_with_password(self, name: str, email: str, password_hash: str) -> Optional[int]:
        """Create new user with hashed password, returns user_id or None if exists"""
        try:
            result = self.client.table("users").select("user_id").eq("email", email).execute()
            
            if result.data:
                logger.warning(f"User already exists with email: {email}")
                return None
            
            result = self.client.table("users").insert({
                "name": name,
                "email": email,
                "password_hash": password_hash
            }).execute()
            
            logger.info(f"Created new user with authentication: {email}")
            return result.data[0]["user_id"]
        except Exception as e:
            logger.error(f"Error in create_user_with_password: {str(e)}")
            return None
    
    def get_user_by_email(self, email: str) -> Optional[Dict]:
        """Fetch user data by email"""
        try:
            result = self.client.table("users").select("*").eq("email", email).execute()
            
            if result.data:
                return result.data[0]
            return None
        except Exception as e:
            logger.error(f"Error in get_user_by_email: {str(e)}")
            return None
    
    def get_or_create_company(self, name: str, industry: str = None, location: str = None, logo_url: str = None) -> Optional[int]:
        """Get existing company or create new one"""
        try:
            result = self.client.table("companies").select("company_id").eq("name", name).execute()
            
            if result.data:
                return result.data[0]["company_id"]
            
            result = self.client.table("companies").insert({
                "name": name,
                "industry": industry,
                "location": location,
                "logo_url": logo_url
            }).execute()
            
            logger.info(f"Created new company: {name}")
            return result.data[0]["company_id"]
        except Exception as e:
            logger.error(f"Error in get_or_create_company: {str(e)}")
            return None
    
    def get_or_create_job(self, company_id: int, title: str, job_type: str = None, 
                          location: str = None, posted_date: datetime = None) -> Optional[int]:
        """Get existing job or create new one"""
        try:
            result = self.client.table("jobs").select("job_id").eq(
                "company_id", company_id
            ).eq("title", title).execute()
            
            if result.data:
                return result.data[0]["job_id"]
            
            job_data = {
                "company_id": company_id,
                "title": title,
                "job_type": job_type,
                "location": location
            }
            
            if posted_date:
                job_data["posted_date"] = posted_date.isoformat()
            
            result = self.client.table("jobs").insert(job_data).execute()
            
            logger.info(f"Created new job: {title} at company_id {company_id}")
            return result.data[0]["job_id"]
        except Exception as e:
            logger.error(f"Error in get_or_create_job: {str(e)}")
            return None
    
    
    def create_application(self, job_id: int, user_id: int, status_date,
                          current_status: str, notes: str = None) -> bool:
        """Create application and log status history"""
        try:
            if current_status not in VALID_STATUSES:
                logger.error(f"Invalid status: {current_status}")
                return False
            
            result = self.client.table("applications").insert({
                "job_id": job_id,
                "user_id": user_id,
                "status_changed_date": status_date.isoformat() if hasattr(status_date, 'isoformat') else status_date,
                "current_status": current_status,
                "notes": notes
            }).execute()
            
            application_id = result.data[0]["application_id"]
            
            if current_status == "Saved":
                self.log_status_change(application_id, "Saved", status_date, notes or "")
            else:
                self.log_status_change(application_id, "Saved", status_date, "")
                self.log_status_change(application_id, current_status, status_date, notes or "")
            
            logger.info(f"Created application {application_id}")
            return True
        except Exception as e:
            logger.error(f"Error creating application: {str(e)}")
            return False
    
    def get_all_applications(self, user_id: int = None, status_filter: str = None) -> List[Dict]:
        """Get all applications for a user with joined data"""
        try:
            query = self.client.table("applications").select(
                "*, jobs(*, companies(*)), users(*)"
            )
            if user_id is not None:
                query = query.eq("user_id", user_id)
            if status_filter and status_filter != "All":
                query = query.eq("current_status", status_filter)
            result = query.order("status_changed_date", desc=True).execute()
            return result.data
        except Exception as e:
            logger.error(f"Error fetching applications: {str(e)}")
            return []
    
    def update_application_status(self, application_id: int, new_status: str, status_date, notes: str = None) -> bool:
        """Update application status and log the change"""
        try:
            if new_status not in VALID_STATUSES:
                logger.error(f"Invalid status: {new_status}")
                return False
            
            self.client.table("applications").update({
                "current_status": new_status,
                "status_changed_date": status_date.isoformat() if hasattr(status_date, 'isoformat') else status_date
            }).eq("application_id", application_id).execute()
            
            self.log_status_change(application_id, new_status, status_date, notes)
            
            logger.info(f"Updated application {application_id} to status {new_status}")
            return True
        except Exception as e:
            logger.error(f"Error updating application status: {str(e)}")
            return False
    
    def delete_application(self, application_id: int) -> bool:
        """Delete application and cascade to status_history"""
        try:
            self.client.table("applications").delete().eq("application_id", application_id).execute()
            
            logger.info(f"Deleted application {application_id}")
            return True
        except Exception as e:
            logger.error(f"Error deleting application: {str(e)}")
            return False
    
    def calculate_ghosted_days(self, status_changed_date_str: str) -> int:
        """Calculate days since status was last changed"""
        try:
            status_changed_date = datetime.fromisoformat(status_changed_date_str.replace('Z', '+00:00'))
            days_passed = (datetime.now(status_changed_date.tzinfo) - status_changed_date).days
            return days_passed
        except Exception as e:
            logger.error(f"Error calculating ghosted days: {str(e)}")
            return 0
    
    
    def log_status_change(self, application_id: int, status: str, status_date, notes: str = None):
        """Log a status change in history"""
        try:
            self.client.table("status_history").insert({
                "application_id": application_id,
                "status": status,
                "status_date": status_date.isoformat() if hasattr(status_date, 'isoformat') else status_date,
                "notes": notes
            }).execute()
            
            logger.info(f"Logged status change for application {application_id}: {status}")
        except Exception as e:
            logger.error(f"Error logging status change: {str(e)}")
    
    def get_status_history(self, application_id: int) -> List[Dict]:
        """Get status history for an application"""
        try:
            result = self.client.table("status_history").select("*").eq(
                "application_id", application_id
            ).order("status_date", desc=True).execute()
            
            return result.data
        except Exception as e:
            logger.error(f"Error fetching status history: {str(e)}")
            return []
    
    
    def get_application_stats(self, user_id: int = None, applications: List[Dict] = None) -> Dict:
        """Get application summary statistics"""
        try:
            if applications is None:
                query = self.client.table("applications").select("current_status")
                if user_id is not None:
                    query = query.eq("user_id", user_id)
                result = query.execute()
                applications = result.data
            
            stats = {
                "total": len(applications),
                "by_status": {}
            }
            for status in VALID_STATUSES:
                count = sum(1 for app in applications if app["current_status"] == status)
                stats["by_status"][status] = count
            return stats
        except Exception as e:
            logger.error(f"Error fetching application stats: {str(e)}")
            return {"total": 0, "by_status": {}}
    
    def get_performance_metrics(self, user_id: int = None, applications: List[Dict] = None, status_history_map: Dict = None) -> Dict:
        """Calculate response time and longest waiting period"""
        try:
            if applications is None:
                applications = self.get_all_applications(user_id)
            
            if not applications:
                return {"response_time": 0.0, "longest_waiting": 0}
            
            response_times = []
            max_waiting_days = 0
            
            for app in applications:
                current_status = app['current_status']
                app_id = app['application_id']
                
                if status_history_map and app_id in status_history_map:
                    status_history = status_history_map[app_id]
                else:
                    status_history = self.get_status_history(app_id)
                
                applied_status = next((s for s in status_history if s['status'] == 'Applied'), None)
                if applied_status:
                    applied_date = datetime.fromisoformat(applied_status['status_date'].replace('Z', '+00:00'))
                    
                    if current_status == 'Applied':
                        days_waiting = (datetime.now(applied_date.tzinfo) - applied_date).days
                        max_waiting_days = max(max_waiting_days, days_waiting)
                    elif current_status in ['Interview', 'Offer', 'Rejected']:
                        current_date = datetime.fromisoformat(app['status_changed_date'].replace('Z', '+00:00'))
                        response_time_days = (current_date - applied_date).days
                        response_times.append(response_time_days)
            
            avg_response_time = sum(response_times) / len(response_times) if response_times else 0
            
            return {
                "response_time": round(avg_response_time, 1),
                "longest_waiting": max_waiting_days
            }
        except Exception as e:
            logger.error(f"Error calculating performance metrics: {str(e)}")
            return {"response_time": 0.0, "longest_waiting": 0}
    
    def get_volume_metrics(self, user_id: int = None, applications: List[Dict] = None) -> Dict:
        """Calculate application volume and submission rates"""
        try:
            if applications is None:
                applications = self.get_all_applications(user_id)
            
            if not applications:
                return {
                    "total_applications": 0,
                    "most_active_day": "N/A",
                    "most_active_count": 0,
                    "rate_per_day": 0,
                    "rate_per_week": 0,
                    "rate_per_month": 0,
                    "rate_per_year": 0
                }
            
            total_apps = len(applications)
            
            day_counts = {}
            for app in applications:
                try:
                    date = datetime.fromisoformat(app['status_changed_date'].replace('Z', '+00:00'))
                    day_name = date.strftime('%A')
                    day_counts[day_name] = day_counts.get(day_name, 0) + 1
                except:
                    continue
            
            most_active_day = max(day_counts, key=day_counts.get) if day_counts else "N/A"
            most_active_count = day_counts.get(most_active_day, 0) if day_counts else 0
            
            if applications:
                dates = []
                for app in applications:
                    try:
                        date = datetime.fromisoformat(app['status_changed_date'].replace('Z', '+00:00'))
                        dates.append(date)
                    except:
                        continue
                
                if dates:
                    oldest = min(dates)
                    newest = max(dates)
                    days_span = max(1, (newest - oldest).days + 1)
                    rate_per_day = total_apps / days_span
                    
                    return {
                        "total_applications": total_apps,
                        "most_active_day": most_active_day,
                        "most_active_count": most_active_count,
                        "rate_per_day": round(rate_per_day, 1),
                        "rate_per_week": round(rate_per_day * 7, 1),
                        "rate_per_month": round(rate_per_day * 30, 1),
                        "rate_per_year": round(rate_per_day * 365, 1)
                    }
            
            return {
                "total_applications": total_apps,
                "most_active_day": most_active_day,
                "most_active_count": most_active_count,
                "rate_per_day": 0,
                "rate_per_week": 0,
                "rate_per_month": 0,
                "rate_per_year": 0
            }
        except Exception as e:
            logger.error(f"Error calculating volume metrics: {str(e)}")
            return {"total_applications": 0, "most_active_day": "N/A", "most_active_count": 0,
                    "rate_per_day": 0, "rate_per_week": 0, "rate_per_month": 0, "rate_per_year": 0}
    
    def get_conversion_funnel(self, user_id: int = None, applications: List[Dict] = None) -> Dict:
        """Get conversion funnel percentages"""
        try:
            if applications is None:
                applications = self.get_all_applications(user_id)
            
            if not applications:
                return {
                    "applied_to_interview": 0.0,
                    "interview_to_offer": 0.0
                }
            
            status_counts = {}
            for app in applications:
                status = app.get('current_status')
                status_counts[status] = status_counts.get(status, 0) + 1
            
            applied_count = sum(status_counts.get(s, 0) for s in ['Applied', 'Interview', 'Offer', 'Rejected'])
            interview_count = status_counts.get('Interview', 0)
            offer_count = status_counts.get('Offer', 0)
            
            total_interviewed = interview_count + offer_count
            
            applied_to_interview = (total_interviewed / applied_count * 100) if applied_count > 0 else 0.0
            interview_to_offer = (offer_count / total_interviewed * 100) if total_interviewed > 0 else 0.0
            
            return {
                "applied_to_interview": round(applied_to_interview, 0),
                "interview_to_offer": round(interview_to_offer, 0)
            }
        except Exception as e:
            logger.error(f"Error calculating conversion funnel: {str(e)}")
            return {"applied_to_interview": 0.0, "interview_to_offer": 0.0}
    
    def get_sankey_data(self, user_id: int = None, applications: List[Dict] = None, status_history_map: Dict = None) -> Dict:
        """Get data for Sankey diagram showing application flow"""
        try:
            if applications is None:
                applications = self.get_all_applications(user_id)
            
            if not applications:
                return {
                    "labels": ["APPLIED (0)", "REJECTED (0)", "GHOSTED (0)", "OFFER (0)", "INTERVIEWING (0)"],
                    "sources": [],
                    "targets": [],
                    "values": [],
                    "colors": [],
                    "counts": {"applied": 0, "rejected": 0, "ghosted": 0, "interviewing": 0, "offer": 0}
                }
            
            applied_apps = [a for a in applications if a.get('current_status') != 'Saved']
            
            if not applied_apps:
                return {
                    "labels": ["APPLIED (0)", "REJECTED (0)", "GHOSTED (0)", "OFFER (0)", "INTERVIEWING (0)"],
                    "sources": [],
                    "targets": [],
                    "values": [],
                    "colors": [],
                    "counts": {"applied": 0, "rejected": 0, "ghosted": 0, "interviewing": 0, "offer": 0}
                }
            
            status_counts = {}
            for app in applied_apps:
                status = app.get('current_status')
                status_counts[status] = status_counts.get(status, 0) + 1
            
            rejected_count = status_counts.get('Rejected', 0)
            applied_current = status_counts.get('Applied', 0)
            interview_current = status_counts.get('Interview', 0)
            offer_count = status_counts.get('Offer', 0)
            
            total_applied = len(applied_apps)
            total_interviewed = interview_current + offer_count
            ghosted_count = applied_current + interview_current
            
            labels = [
                f"APPLIED ({total_applied})",
                f"REJECTED ({rejected_count})",
                f"GHOSTED ({ghosted_count})",
                f"OFFER ({offer_count})",
                f"INTERVIEWING ({total_interviewed})"
            ]
            
            GHOSTED_COLOR = 'rgba(184, 161, 214, 0.5)'
            REJECTED_COLOR = 'rgba(255, 107, 107, 0.5)'
            INTERVIEWING_COLOR = 'rgba(77, 182, 172, 0.5)'
            OFFER_COLOR = 'rgba(124, 179, 66, 0.5)'
            
            sources, targets, values, colors = [], [], [], []
            
            if applied_current > 0:
                sources.append(0)
                targets.append(2)
                values.append(applied_current)
                colors.append(GHOSTED_COLOR)
            
            if rejected_count > 0:
                sources.append(0)
                targets.append(1)
                values.append(rejected_count)
                colors.append(REJECTED_COLOR)
            
            if total_interviewed > 0:
                sources.append(0)
                targets.append(4)
                values.append(total_interviewed)
                colors.append(INTERVIEWING_COLOR)
            
            if offer_count > 0:
                sources.append(4)
                targets.append(3)
                values.append(offer_count)
                colors.append(OFFER_COLOR)
            
            if interview_current > 0:
                sources.append(4)
                targets.append(2)
                values.append(interview_current)
                colors.append(GHOSTED_COLOR)
            
            return {
                "labels": labels,
                "sources": sources,
                "targets": targets,
                "values": values,
                "colors": colors,
                "counts": {
                    "applied": total_applied,
                    "rejected": rejected_count,
                    "ghosted": ghosted_count,
                    "offer": offer_count,
                    "interviewing": total_interviewed
                }
            }
        except Exception as e:
            logger.error(f"Error generating Sankey data: {str(e)}")
            return {"labels": [], "sources": [], "targets": [], "values": [], "colors": [], "counts": {}}
