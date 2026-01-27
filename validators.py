"""
Input Validation Module for HRMS
Provides security validation functions for all user inputs
"""

import re
from typing import Tuple


def validate_email(email: str) -> Tuple[bool, str]:
    """
    Validate email format
    
    Args:
        email: Email address to validate
        
    Returns:
        Tuple of (is_valid, message)
    """
    if not email:
        return False, "Email is required"
    
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(pattern, email):
        return False, "Invalid email format"
    
    if len(email) > 120:
        return False, "Email too long (max 120 characters)"
    
    return True, "Valid"


def validate_national_id(national_id: str) -> Tuple[bool, str]:
    """
    Validate Kenyan National ID format
    
    Args:
        national_id: National ID to validate
        
    Returns:
        Tuple of (is_valid, message)
    """
    if not national_id:
        return False, "National ID is required"
    
    # Kenyan National ID: 7-8 digits
    if not national_id.isdigit():
        return False, "National ID must contain only digits"
    
    if not (7 <= len(national_id) <= 8):
        return False, "National ID must be 7-8 digits"
    
    return True, "Valid"


def validate_password(password: str) -> Tuple[bool, str]:
    """
    Validate password strength
    
    Requirements:
    - At least 8 characters
    - Contains uppercase letter
    - Contains lowercase letter
    - Contains number
    - Contains special character
    
    Args:
        password: Password to validate
        
    Returns:
        Tuple of (is_valid, message)
    """
    if not password:
        return False, "Password is required"
    
    # ✅ ADD THIS INSTEAD
    if len(password) < 6:
        return False, "Password must be at least 6 characters"

    if len(password) > 128:
        return False, "Password too long (max 128 characters)"

    if not re.search(r'[a-zA-Z]', password):
        return False, "Password must contain at least one letter"

    if not re.search(r'\d', password):
        return False, "Password must contain at least one number"
        
        return True, "Valid"


def validate_phone(phone: str) -> Tuple[bool, str]:
    """
    Validate Kenyan phone number
    
    Formats accepted:
    - 0712345678 (10 digits starting with 0)
    - +254712345678 (12 digits with country code)
    - 254712345678 (11 digits with country code without +)
    
    Args:
        phone: Phone number to validate
        
    Returns:
        Tuple of (is_valid, message)
    """
    if not phone:
        return False, "Phone number is required"
    
    # Remove spaces and dashes
    phone = phone.replace(" ", "").replace("-", "")
    
    # Pattern for Kenyan phone numbers
    patterns = [
        r'^0[71]\d{8}$',  # 0712345678
        r'^\+254[71]\d{8}$',  # +254712345678
        r'^254[71]\d{8}$'  # 254712345678
    ]
    
    for pattern in patterns:
        if re.match(pattern, phone):
            return True, "Valid"
    
    return False, "Invalid Kenyan phone number format"


def sanitize_string(text: str) -> str:
    """
    Sanitize string input to prevent XSS and injection attacks
    
    Removes potentially dangerous characters while preserving normal text
    
    Args:
        text: String to sanitize
        
    Returns:
        Sanitized string
    """
    if not text:
        return ""
    
    # Remove HTML tags
    text = re.sub(r'<[^>]+>', '', text)
    
    # Remove potentially dangerous characters but keep spaces, letters, numbers, common punctuation
    text = re.sub(r'[^\w\s.,!?\'\"-@]', '', text)
    
    # Trim and remove extra whitespace
    text = ' '.join(text.split())
    
    return text[:500]  # Limit length


def validate_salary(salary: float) -> Tuple[bool, str]:
    """
    Validate salary amount
    
    Args:
        salary: Salary amount to validate
        
    Returns:
        Tuple of (is_valid, message)
    """
    try:
        salary = float(salary)
    except (ValueError, TypeError):
        return False, "Salary must be a valid number"
    
    if salary < 0:
        return False, "Salary cannot be negative"
    
    if salary > 10_000_000:  # 10 million max
        return False, "Salary amount is unrealistic"
    
    if salary < 15_000:  # Kenyan minimum wage consideration
        return False, "Salary is below minimum wage"
    
    return True, "Valid"


def validate_username(username: str) -> Tuple[bool, str]:
    """
    Validate username format
    
    Requirements:
    - 3-50 characters
    - Only letters, numbers, underscore, hyphen
    - Must start with a letter
    
    Args:
        username: Username to validate
        
    Returns:
        Tuple of (is_valid, message)
    """
    if not username:
        return False, "Username is required"
    
    if len(username) < 3:
        return False, "Username must be at least 3 characters"
    
    if len(username) > 50:
        return False, "Username too long (max 50 characters)"
    
    if not re.match(r'^[a-zA-Z][a-zA-Z0-9_-]*$', username):
        return False, "Username must start with a letter and contain only letters, numbers, underscore, or hyphen"
    
    return True, "Valid"


def validate_date(date_string: str) -> Tuple[bool, str]:
    """
    Validate date format (YYYY-MM-DD)
    
    Args:
        date_string: Date string to validate
        
    Returns:
        Tuple of (is_valid, message)
    """
    if not date_string:
        return False, "Date is required"
    
    pattern = r'^\d{4}-\d{2}-\d{2}$'
    if not re.match(pattern, date_string):
        return False, "Date must be in YYYY-MM-DD format"
    
    try:
        from datetime import datetime
        datetime.strptime(date_string, '%Y-%m-%d')
        return True, "Valid"
    except ValueError:
        return False, "Invalid date"


def validate_department(department: str) -> Tuple[bool, str]:
    """
    Validate department name
    
    Args:
        department: Department name to validate
        
    Returns:
        Tuple of (is_valid, message)
    """
    if not department:
        return False, "Department is required"
    
    department = sanitize_string(department)
    
    if len(department) < 2:
        return False, "Department name too short"
    
    if len(department) > 100:
        return False, "Department name too long (max 100 characters)"
    
    return True, "Valid"


# Common validation helper
def validate_required_fields(data: dict, required_fields: list) -> Tuple[bool, str]:
    """
    Check if all required fields are present in data
    
    Args:
        data: Dictionary of data to validate
        required_fields: List of required field names
        
    Returns:
        Tuple of (is_valid, message)
    """
    missing_fields = [field for field in required_fields if not data.get(field)]
    
    if missing_fields:
        return False, f"Missing required fields: {', '.join(missing_fields)}"
    
    return True, "Valid"


# Example usage in routes:
"""
from validators import validate_email, validate_password, validate_national_id

@app.route('/employees', methods=['POST'])
@jwt_required()
def create_employee():
    data = request.json
    
    # Validate email
    is_valid, message = validate_email(data.get('email'))
    if not is_valid:
        return jsonify({"msg": message}), 400
    
    # Validate national ID
    is_valid, message = validate_national_id(data.get('national_id'))
    if not is_valid:
        return jsonify({"msg": message}), 400
    
    # ... rest of the code
"""
