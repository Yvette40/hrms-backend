#!/usr/bin/env python3
"""
HRMS Employee Profile API Response Tester
==========================================
This script simulates what data different users would receive when
accessing the /api/employee/profile endpoint.

Usage:
    python test_profile_api.py
"""

import sys
import os
import json

# Add the current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app
from models import User, Employee

def print_header(text):
    """Print a formatted header"""
    print(f"\n{'='*80}")
    print(f"  {text}")
    print(f"{'='*80}\n")

def print_section(text):
    """Print a section header"""
    print(f"\n{text}")
    print("-" * 80)

def simulate_profile_api_response(username):
    """
    Simulate what the /api/employee/profile endpoint would return for a given user.
    This replicates the logic in app.py line 1979-2064
    """
    user = User.query.filter_by(username=username).first()
    
    if not user:
        return None, {'error': 'User not found'}
    
    # Get the linked employee profile
    employee = None
    if hasattr(user, 'employee_profile'):
        if isinstance(user.employee_profile, list):
            employee = user.employee_profile[0] if user.employee_profile else None
        else:
            employee = user.employee_profile
    
    # Also try to find by user_id
    if not employee:
        employee = Employee.query.filter_by(user_id=user.id).first()
    
    if not employee:
        # No employee profile linked - return basic user data
        return False, {
            'first_name': user.username.split()[0] if ' ' in user.username else user.username,
            'last_name': user.username.split()[1] if len(user.username.split()) > 1 else '',
            'email': user.email or '',
            'phone': user.phone or '',
            'department': 'General',
            'position': user.role.replace('_', ' ').title(),
            'employee_id': 'N/A',
            'date_joined': user.created_at.strftime('%B %d, %Y') if user.created_at else '',
            'address': '',
            'emergency_contact': '',
            'emergency_name': ''
        }
    
    # Return complete employee profile
    profile_data = {
        'id': employee.id,
        'employee_id': employee.national_id,
        'first_name': employee.name.split()[0] if employee.name else '',
        'last_name': ' '.join(employee.name.split()[1:]) if len(employee.name.split()) > 1 else '',
        'email': employee.email or user.email or '',
        'phone': employee.phone_number or user.phone or '',
        'department': employee.department or 'General',
        'position': employee.position or 'Employee',
        'job_title': employee.position or 'Employee',
        'date_joined': employee.join_date.strftime('%B %d, %Y') if employee.join_date else '',
        'hire_date': employee.join_date.strftime('%Y-%m-%d') if employee.join_date else '',
        'address': getattr(employee, 'address', ''),
        'emergency_contact': getattr(employee, 'emergency_contact', ''),
        'emergency_phone': getattr(employee, 'emergency_contact', ''),
        'emergency_name': getattr(employee, 'emergency_name', ''),
        'emergency_contact_name': getattr(employee, 'emergency_name', ''),
        'leave_balance': employee.leave_balance or 0,
        'base_salary': employee.base_salary,
        'active': employee.active
    }
    
    return True, profile_data

def test_user_profile(username):
    """Test and display the profile response for a specific user"""
    print(f"\n{'▶'*40}")
    print(f"Testing User: {username}")
    print(f"{'▶'*40}")
    
    has_employee, response = simulate_profile_api_response(username)
    
    if response is None:
        print("❌ User not found in database")
        return False
    
    if 'error' in response:
        print(f"❌ Error: {response['error']}")
        return False
    
    if has_employee:
        print("✅ Status: User HAS employee profile")
    else:
        print("⚠️  Status: User has NO employee profile (fallback data returned)")
    
    print("\n📄 API Response Data:")
    print(json.dumps(response, indent=2, default=str))
    
    # Analyze the quality of the data
    print("\n🔍 Data Quality Analysis:")
    
    critical_fields = {
        'employee_id': response.get('employee_id'),
        'first_name': response.get('first_name'),
        'last_name': response.get('last_name'),
        'email': response.get('email'),
        'phone': response.get('phone'),
        'department': response.get('department'),
        'position': response.get('position')
    }
    
    empty_count = 0
    for field, value in critical_fields.items():
        if not value or value == 'N/A':
            print(f"   ⚠️  {field:20s}: MISSING or N/A")
            empty_count += 1
        else:
            print(f"   ✓  {field:20s}: {str(value)[:40]}")
    
    if empty_count > 0:
        print(f"\n   ⚠️  Warning: {empty_count} critical field(s) are missing!")
    else:
        print(f"\n   ✅ All critical fields have data!")
    
    return has_employee

def test_all_problematic_users():
    """Test all users known to have profile issues"""
    print_header("Testing All Problematic Users")
    
    test_users = ['admin', 'hr_officer', 'dept_manager', 'employee', 'jmwangi']
    
    results = {}
    for username in test_users:
        has_profile = test_user_profile(username)
        results[username] = has_profile
    
    # Summary
    print_section("📊 Test Summary")
    
    working = sum(1 for v in results.values() if v)
    not_working = sum(1 for v in results.values() if not v)
    
    print(f"Total Users Tested:     {len(results)}")
    print(f"✅ With Employee Profile: {working}")
    print(f"❌ WITHOUT Profile:       {not_working}")
    
    if not_working > 0:
        print(f"\n⚠️  Users that cannot view their full profile:")
        for username, has_profile in results.items():
            if not has_profile:
                print(f"   - {username}")

def test_working_user_sample():
    """Test a sample of users that should be working"""
    print_header("Testing Sample of Working Users")
    
    # Get first 3 users with employee profiles
    from sqlalchemy import and_
    working_users = User.query.join(
        Employee, User.id == Employee.user_id
    ).limit(3).all()
    
    if not working_users:
        print("No working users found!")
        return
    
    for user in working_users:
        test_user_profile(user.username)

def show_comparison():
    """Show side-by-side comparison of working vs non-working profiles"""
    print_header("Working vs Non-Working Profile Comparison")
    
    # Find a working user
    working_user = User.query.join(
        Employee, User.id == Employee.user_id
    ).first()
    
    # Find a non-working user
    non_working_user = User.query.filter_by(username='admin').first()
    
    if working_user:
        print("✅ WORKING EXAMPLE (User with Employee Profile):")
        has_emp, working_data = simulate_profile_api_response(working_user.username)
        print(f"User: {working_user.username}")
        print(f"Fields populated: {sum(1 for v in working_data.values() if v and v != 'N/A')}/{len(working_data)}")
    
    if non_working_user:
        print("\n❌ NON-WORKING EXAMPLE (User without Employee Profile):")
        has_emp, non_working_data = simulate_profile_api_response(non_working_user.username)
        print(f"User: {non_working_user.username}")
        print(f"Fields populated: {sum(1 for v in non_working_data.values() if v and v != 'N/A')}/{len(non_working_data)}")
    
    print("\n🔍 This shows why users without employee profiles see minimal data!")

def main():
    """Main test function"""
    print_header("HRMS Employee Profile API Response Tester")
    print("This script simulates API responses for different users to help diagnose")
    print("why employee profiles may not be fetching data correctly.\n")
    
    print("Choose a test mode:")
    print("  1. Test specific user")
    print("  2. Test all problematic users")
    print("  3. Test sample of working users")
    print("  4. Show working vs non-working comparison")
    print("  5. Run all tests")
    
    choice = input("\nEnter choice (1-5): ").strip()
    
    with app.app_context():
        try:
            if choice == '1':
                username = input("Enter username to test: ").strip()
                test_user_profile(username)
            
            elif choice == '2':
                test_all_problematic_users()
            
            elif choice == '3':
                test_working_user_sample()
            
            elif choice == '4':
                show_comparison()
            
            elif choice == '5':
                test_all_problematic_users()
                test_working_user_sample()
                show_comparison()
            
            else:
                print("Invalid choice!")
                return
            
            # Final message
            print_header("Testing Complete")
            print("If you found users with missing profile data, run:")
            print("   python fix_employee_profiles.py")
            print("\nTo fix the issues automatically.")
            
        except Exception as e:
            print(f"\n❌ ERROR: {str(e)}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    main()
