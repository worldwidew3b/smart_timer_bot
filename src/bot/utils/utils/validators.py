from typing import Optional
import re


def validate_task_title(title: str) -> tuple[bool, str]:
    """
    Validate task title
    Returns (is_valid, error_message)
    """
    if not title or len(title.strip()) == 0:
        return False, "Title cannot be empty"
    
    if len(title) > 200:
        return False, "Title is too long (max 200 characters)"
    
    return True, ""


def validate_task_description(description: Optional[str]) -> tuple[bool, str]:
    """
    Validate task description
    Returns (is_valid, error_message)
    """
    if description is None:
        return True, ""
    
    if len(description) > 1000:
        return False, "Description is too long (max 1000 characters)"
    
    return True, ""


def validate_estimated_time(estimated_time: int) -> tuple[bool, str]:
    """
    Validate estimated time in minutes
    Returns (is_valid, error_message)
    """
    if estimated_time <= 0:
        return False, "Estimated time must be greater than 0"
    
    if estimated_time > 9999:  # Max 9999 minutes (~7 days)
        return False, "Estimated time is too long (max 9999 minutes)"
    
    return True, ""


def validate_priority(priority: int) -> tuple[bool, str]:
    """
    Validate task priority (1-5)
    Returns (is_valid, error_message)
    """
    if priority < 1 or priority > 5:
        return False, "Priority must be between 1 and 5"
    
    return True, ""


def validate_tag_name(name: str) -> tuple[bool, str]:
    """
    Validate tag name
    Returns (is_valid, error_message)
    """
    if not name or len(name.strip()) == 0:
        return False, "Tag name cannot be empty"
    
    if len(name) > 50:
        return False, "Tag name is too long (max 50 characters)"
    
    # Check for valid characters (alphanumeric, spaces, hyphens, underscores)
    if not re.match(r'^[\w\s\-_]+$', name):
        return False, "Tag name contains invalid characters"
    
    return True, ""


def validate_telegram_id(telegram_id: str) -> tuple[bool, str]:
    """
    Validate Telegram ID
    Returns (is_valid, error_message)
    """
    if not telegram_id:
        return False, "Telegram ID cannot be empty"
    
    try:
        int(telegram_id)
        return True, ""
    except ValueError:
        return False, "Telegram ID must be a number"