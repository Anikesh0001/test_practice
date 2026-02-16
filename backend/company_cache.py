"""
Company Profile Cache System
Manages local storage of company hiring profiles to avoid redundant API calls
"""
import os
import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

# Cache directory path
CACHE_DIR = Path("data/company_profiles")


def _ensure_cache_directory():
    """Create cache directory if it doesn't exist."""
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    logger.info(f"Cache directory ensured at: {CACHE_DIR}")


def _get_cache_file_path(company_name: str) -> Path:
    """
    Get the cache file path for a company.
    
    Args:
        company_name: Name of the company
        
    Returns:
        Path object for the cache file
    """
    # Sanitize company name for filename
    safe_name = "".join(c if c.isalnum() else "_" for c in company_name.lower())
    return CACHE_DIR / f"{safe_name}.json"


def get_company_profile(company_name: str) -> Optional[Dict[str, Any]]:
    """
    Load company profile from cache if it exists.
    
    Args:
        company_name: Name of the company
        
    Returns:
        Company profile dict if cached, None otherwise
    """
    _ensure_cache_directory()
    
    cache_file = _get_cache_file_path(company_name)
    
    if not cache_file.exists():
        logger.info(f"No cache found for company: {company_name}")
        return None
    
    try:
        with open(cache_file, "r", encoding="utf-8") as f:
            profile = json.load(f)
        
        logger.info(f"Loaded cached profile for company: {company_name}")
        return profile
        
    except (json.JSONDecodeError, IOError) as e:
        logger.error(f"Error reading cache for {company_name}: {e}")
        return None


def save_company_profile(company_name: str, profile: Dict[str, Any]) -> bool:
    """
    Save company profile to cache.
    
    Args:
        company_name: Name of the company
        profile: Company profile data to cache
        
    Returns:
        True if save successful, False otherwise
    """
    _ensure_cache_directory()
    
    # Add metadata
    profile["cached_at"] = datetime.utcnow().isoformat()
    profile["cache_version"] = "1.0"
    
    cache_file = _get_cache_file_path(company_name)
    
    try:
        with open(cache_file, "w", encoding="utf-8") as f:
            json.dump(profile, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Saved profile to cache for company: {company_name}")
        return True
        
    except IOError as e:
        logger.error(f"Error saving cache for {company_name}: {e}")
        return False


def list_cached_companies() -> list[str]:
    """
    Get list of all cached company names.
    
    Returns:
        List of cached company names
    """
    _ensure_cache_directory()
    
    cached = []
    for cache_file in CACHE_DIR.glob("*.json"):
        try:
            with open(cache_file, "r", encoding="utf-8") as f:
                profile = json.load(f)
                cached.append(profile.get("company_name", cache_file.stem))
        except Exception as e:
            logger.warning(f"Error reading cache file {cache_file}: {e}")
    
    return sorted(cached)


def delete_company_profile(company_name: str) -> bool:
    """
    Delete a company profile from cache.
    
    Args:
        company_name: Name of the company
        
    Returns:
        True if deleted, False if not found or error
    """
    cache_file = _get_cache_file_path(company_name)
    
    if not cache_file.exists():
        logger.warning(f"No cache to delete for company: {company_name}")
        return False
    
    try:
        cache_file.unlink()
        logger.info(f"Deleted cache for company: {company_name}")
        return True
    except Exception as e:
        logger.error(f"Error deleting cache for {company_name}: {e}")
        return False


async def get_or_fetch_profile(company_name: str, fetch_func) -> Dict[str, Any]:
    """
    Get company profile from cache or fetch if not cached.
    
    Args:
        company_name: Name of the company
        fetch_func: Async function to fetch profile if not cached
        
    Returns:
        Company profile dictionary
    """
    # Try to load from cache first
    profile = get_company_profile(company_name)
    
    if profile:
        logger.info(f"Using cached profile for: {company_name}")
        return profile
    
    # If not cached, fetch using provided function
    logger.info(f"Fetching new profile for: {company_name}")
    profile = await fetch_func(company_name)
    
    # Save to cache
    save_company_profile(company_name, profile)
    
    return profile
