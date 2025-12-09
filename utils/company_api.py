"""
Company API Integration
Fetch company data from Simplify Jobs API
"""

import requests
import logging

logger = logging.getLogger(__name__)

SIMPLIFY_API_BASE = "https://api.simplify.jobs/v2/company/"


def search_companies(query, page=0):
    """Search companies using Simplify Jobs API, returns list of company dicts"""
    try:
        url = f"{SIMPLIFY_API_BASE}?page={page}&value={query}"
        response = requests.get(url, timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            
            if isinstance(data, dict) and 'items' in data:
                companies = data['items']
            elif isinstance(data, dict) and 'data' in data:
                companies = data['data']
            elif isinstance(data, list):
                companies = data
            else:
                companies = []
            
            logger.info(f"Found {len(companies)} companies for query: {query}")
            return companies
        else:
            logger.error(f"API request failed with status {response.status_code}")
            return []
            
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching companies from API: {str(e)}")
        return []
    except Exception as e:
        logger.error(f"Unexpected error in company search: {str(e)}")
        return []


def get_company_by_name(company_name):
    """
    Get company details by exact or partial name match
    
    Args:
        company_name (str): Company name to search
    
    Returns:
        dict: Company data with name, logo, etc. or None if not found
    """
    companies = search_companies(company_name)
    
    if companies and len(companies) > 0:
        return companies[0]
    
    return None
