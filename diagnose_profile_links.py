#!/usr/bin/env python3
"""
HRMS Employee Profile Diagnostic Script
========================================
This script checks the status of user-employee links without making any changes.
Use this to diagnose profile data fetching issues.

Usage:
    python diagnose_profile_links.py
"""

import sys
import os

# Add the current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from models import User, Employee
from sqlalchemy import func

def print_header(text):
    """Print a formatted header"""
    print(f"\n{'='*80}")
    print(f"  {text}")
    print(f"{'='*80}\n")

def print_section(text):
    """Print a section header"""
    print(f"\n{text}")
    print("-" * 80)

def check_database_stats():
    """Check overall database statistics"""
    print_section("📊 Database Statistics")
    
    user_count = User.query.count()
    employee_count = Employee.query.count()
    linked_employees = Employee.query.filter(Employee.user_id.isnot(None)).count()
    unlinked_employees = Employee.query.filter(Employee.user_id.is_(None)).count()
    
    print(f"Total Users:                    {user_count}")
    print(f"Total Employees:                {employee_count}")
    print(f"Employees Linked to Users:      {linked_employees}")
    print(f"Employees NOT Linked to Users:  {unlinked_employees}")

def check_users_without_profiles():
    """Find all users without employee profiles"""
    print_section("❌ Users WITHOUT Employee Profiles")
    
    all_users = User.query.all()
    users_without_profiles = []
    
    for user in all_users:
        employee = Employee.query.filter_by(user_id=user.id).first()
        if not employee:
            users_without_profiles.append(user)
    
    if not users_without_profiles:
        print("✅ All users have employee profiles!")
        return []
    
    print(f"Found {len(users_without_profiles)} user(s) without employee profiles:\n")
    
    for user in users_without_profiles:
        print(f"User ID: {user.id:3d}  |  Username: {user.username:20s}  |  Role: {user.role:20s}")
        print(f"             Email: {user.email or 'None':30s}  Phone: {user.phone or 'None'}")
        print()
    
    return users_without_profiles

def check_specific_problematic_cases():
    """Check specific known problematic cases"""
    print_section("🔍 Checking Specific Cases")
    
    # Case 1: jmwangi user
    print("Case 1: User 'jmwangi' (ID: 89)")
    jmwangi_user = User.query.get(89)
    if jmwangi_user:
        print(f"  ✓ User exists: {jmwangi_user.username} (email: {jmwangi_user.email})")
        employee = Employee.query.filter_by(user_id=89).first()
        if employee:
            print(f"  ✓ Linked to employee: {employee.name} (ID: {employee.id})")
        else:
            print(f"  ✗ NOT linked to any employee")
            # Check if there's a matching employee by email
            matching = Employee.query.filter_by(email=jmwangi_user.email).first()
            if matching:
                print(f"  ⚠️  Found matching employee by email: {matching.name} (ID: {matching.id})")
                print(f"      This employee is currently linked to user_id: {matching.user_id}")
    else:
        print("  ✗ User not found")
    
    print()
    
    # Case 2: System users
    system_users = ['admin', 'hr_officer', 'dept_manager', 'employee']
    print("Case 2: System Users")
    for username in system_users:
        user = User.query.filter_by(username=username).first()
        if user:
            employee = Employee.query.filter_by(user_id=user.id).first()
            status = "✓ Linked" if employee else "✗ NOT linked"
            emp_info = f" → {employee.name}" if employee else ""
            print(f"  {status}: {username:20s} (ID: {user.id}){emp_info}")
        else:
            print(f"  ✗ User not found: {username}")

def check_employees_without_users():
    """Find employees not linked to any user"""
    print_section("📋 Employees NOT Linked to Users")
    
    unlinked_employees = Employee.query.filter(Employee.user_id.is_(None)).all()
    
    if not unlinked_employees:
        print("✅ All employees are linked to user accounts!")
        return []
    
    print(f"Found {len(unlinked_employees)} employee(s) without user links:\n")
    
    for emp in unlinked_employees[:10]:  # Show first 10
        print(f"Employee ID: {emp.id:3d}  |  Name: {emp.name:30s}")
        print(f"                 Email: {emp.email or 'None':30s}  National ID: {emp.national_id}")
        print()
    
    if len(unlinked_employees) > 10:
        print(f"... and {len(unlinked_employees) - 10} more")
    
    return unlinked_employees

def check_sample_working_profiles():
    """Show some examples of working profiles"""
    print_section("✅ Sample Working User-Employee Links")
    
    linked_users = db.session.query(User, Employee).join(
        Employee, User.id == Employee.user_id
    ).limit(5).all()
    
    if not linked_users:
        print("No linked profiles found!")
        return
    
    for user, employee in linked_users:
        print(f"User: {user.username:20s} (ID: {user.id:3d})  →  Employee: {employee.name:30s} (ID: {employee.id:3d})")
    
    print(f"\n(Showing 5 of many working links)")

def suggest_fixes(users_without_profiles):
    """Suggest fixes based on diagnostic results"""
    print_section("💡 Suggested Fixes")
    
    if not users_without_profiles:
        print("✅ No fixes needed - all users have employee profiles!")
        return
    
    print("To fix the profile fetching issue, you need to:")
    print()
    
    # Check for specific cases
    usernames = [u.username for u in users_without_profiles]
    user_ids = [u.id for u in users_without_profiles]
    
    if 89 in user_ids or 'jmwangi' in usernames:
        print("1. Fix 'jmwangi' user link:")
        print("   This user should be linked to employee 'John Mwangi'")
        print()
    
    system_user_found = any(u in usernames for u in ['admin', 'hr_officer', 'dept_manager', 'employee'])
    if system_user_found:
        print("2. Create employee profiles for system users:")
        print("   Users like 'admin', 'hr_officer' need corresponding employee records")
        print()
    
    print("You can run the fix script to automatically resolve these issues:")
    print("   python fix_employee_profiles.py")
    print()
    print("Or manually create the links using SQL or Python scripts.")

def main():
    """Main diagnostic function"""
    print_header("HRMS Employee Profile Link Diagnostic")
    print("This script analyzes the user-employee relationships in the database.")
    print("No changes will be made - this is read-only diagnostic.\n")
    
    with app.app_context():
        try:
            # Run all diagnostic checks
            check_database_stats()
            users_without_profiles = check_users_without_profiles()
            check_specific_problematic_cases()
            check_employees_without_users()
            check_sample_working_profiles()
            suggest_fixes(users_without_profiles)
            
            # Final summary
            print_header("Diagnostic Summary")
            
            if not users_without_profiles:
                print("✅ GOOD NEWS: All users have employee profiles!")
                print("   If you're still experiencing issues, check:")
                print("   - Frontend API endpoint configuration")
                print("   - JWT token validity")
                print("   - Network connectivity")
            else:
                print(f"⚠️  ISSUE FOUND: {len(users_without_profiles)} user(s) don't have employee profiles")
                print(f"   This is why they cannot see their profile data.")
                print(f"\n   Run 'python fix_employee_profiles.py' to fix these issues.")
            
        except Exception as e:
            print(f"\n❌ ERROR: {str(e)}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    main()
