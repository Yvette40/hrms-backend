#!/usr/bin/env python3
"""
HRMS Real-Time Diagnostic - What's Actually Broken Right Now?
==============================================================
This script checks your CURRENT system state and tells you exactly
what needs to be fixed for attendance and payslips to work.

Usage:
    python diagnose_current_state.py
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from models import User, Employee, Attendance, Payroll
from datetime import datetime, timedelta

def print_header(text):
    print(f"\n{'='*80}")
    print(f"  {text}")
    print(f"{'='*80}\n")

def print_section(text):
    print(f"\n{text}")
    print("-" * 80)

def check_code_bugs():
    """Check if the code bugs are still present"""
    print_section("🔍 Step 1: Checking Code Bugs in app.py")
    
    try:
        with open('app.py', 'r') as f:
            content = f.read()
            lines = content.split('\n')
        
        bugs_found = []
        
        # Check /my-attendance endpoint
        in_my_attendance = False
        attendance_bug = False
        for i, line in enumerate(lines):
            if '@app.route("/my-attendance"' in line:
                in_my_attendance = True
            elif in_my_attendance and 'def get_my_attendance' in line:
                in_my_attendance = True
            elif in_my_attendance and '@app.route' in line and i > 0:
                break
            elif in_my_attendance and 'filter_by(name=user.username)' in line:
                attendance_bug = True
                bugs_found.append(('my-attendance', i+1))
        
        # Check /my-payslips endpoint
        in_my_payslips = False
        payslips_bug = False
        for i, line in enumerate(lines):
            if '@app.route("/my-payslips"' in line:
                in_my_payslips = True
            elif in_my_payslips and 'def get_my_payslips' in line:
                in_my_payslips = True
            elif in_my_payslips and '@app.route' in line and i > 0:
                break
            elif in_my_payslips and 'filter_by(name=user.username)' in line:
                payslips_bug = True
                bugs_found.append(('my-payslips', i+1))
        
        if bugs_found:
            print("❌ CODE BUGS FOUND (CRITICAL!):")
            for endpoint, line_num in bugs_found:
                print(f"   • /{endpoint} at line {line_num}")
                print(f"     Uses: filter_by(name=user.username) ← WRONG!")
            print("\n   ⚠️  This is why attendance and payslips don't work!")
            return False
        else:
            print("✅ Code looks correct (uses filter_by(user_id=user.id))")
            return True
            
    except Exception as e:
        print(f"❌ Error checking code: {str(e)}")
        return False

def check_user_links():
    """Check if users are linked to employees"""
    print_section("🔍 Step 2: Checking User-Employee Links")
    
    # Get current user from JWT or check common test users
    test_users = ['fnjoroge', 'jmwangi', 'vmakokha', 'enjeri', 'admin', 'employee']
    
    problem_users = []
    working_users = []
    
    for username in test_users:
        user = User.query.filter_by(username=username).first()
        if not user:
            continue
        
        employee = Employee.query.filter_by(user_id=user.id).first()
        
        if not employee:
            problem_users.append(username)
        else:
            working_users.append((username, employee.name, employee.id))
    
    if problem_users:
        print(f"❌ Found {len(problem_users)} users WITHOUT employee links:")
        for username in problem_users:
            print(f"   • {username}")
    
    if working_users:
        print(f"\n✅ Found {len(working_users)} users WITH proper links:")
        for username, emp_name, emp_id in working_users[:3]:
            print(f"   • {username} → {emp_name} (Employee ID: {emp_id})")
    
    return len(problem_users) == 0

def test_attendance_query():
    """Simulate what happens when an employee tries to get attendance"""
    print_section("🔍 Step 3: Testing Attendance Query Logic")
    
    # Test with a user we know has data
    test_user = User.query.filter_by(username='fnjoroge').first()
    
    if not test_user:
        print("⚠️  Test user 'fnjoroge' not found. Using another user...")
        test_user = User.query.filter(User.username.like('f%')).first()
    
    if not test_user:
        print("⚠️  No test user available")
        return
    
    print(f"Testing with user: {test_user.username} (ID: {test_user.id})")
    
    # Method 1: Current BROKEN method (by name)
    print("\n❌ Current (Broken) Method: filter_by(name=user.username)")
    employee_by_name = Employee.query.filter_by(name=test_user.username).first()
    if employee_by_name:
        print(f"   Found: {employee_by_name.name}")
        att_count = Attendance.query.filter_by(employee_id=employee_by_name.id).count()
        print(f"   Attendance records: {att_count}")
    else:
        print(f"   NOT FOUND! (username '{test_user.username}' doesn't match any employee name)")
        print(f"   Result: Returns EMPTY array → User sees 'No records found'")
    
    # Method 2: Correct method (by user_id)
    print("\n✅ Correct Method: filter_by(user_id=user.id)")
    employee_by_id = Employee.query.filter_by(user_id=test_user.id).first()
    if employee_by_id:
        print(f"   Found: {employee_by_id.name} (Employee ID: {employee_by_id.id})")
        att_count = Attendance.query.filter_by(employee_id=employee_by_id.id).count()
        print(f"   Attendance records: {att_count}")
        if att_count > 0:
            print(f"   ✅ This data EXISTS but user can't see it due to bug!")
    else:
        print(f"   NOT FOUND (user not linked to employee)")

def check_data_availability():
    """Check if attendance and payroll data actually exists"""
    print_section("🔍 Step 4: Checking Data in Database")
    
    att_count = Attendance.query.count()
    payroll_count = Payroll.query.count()
    
    print(f"Total Attendance Records: {att_count}")
    print(f"Total Payroll Records: {payroll_count}")
    
    if att_count > 0:
        print("\n✅ Attendance data EXISTS in database")
        # Sample
        sample = Attendance.query.limit(3).all()
        for att in sample:
            emp = Employee.query.get(att.employee_id)
            print(f"   • Employee: {emp.name if emp else 'Unknown'}, Date: {att.date}, Status: {att.status}")
    else:
        print("\n⚠️  No attendance data found in database")
    
    if payroll_count > 0:
        print("\n✅ Payroll data EXISTS in database")
    else:
        print("\n⚠️  No payroll data found in database")

def show_exact_problem():
    """Show the exact problem with a real example"""
    print_section("🎯 EXACT PROBLEM (Real Example)")
    
    user = User.query.filter_by(username='fnjoroge').first()
    if not user:
        user = User.query.first()
    
    if not user:
        print("No users in database")
        return
    
    print(f"User Login: {user.username}")
    print(f"User ID: {user.id}")
    
    # Show what the broken code does
    print(f"\n❌ What Current Code Does:")
    print(f"   1. User logs in as '{user.username}'")
    print(f"   2. Code searches: Employee.query.filter_by(name='{user.username}')")
    
    emp_by_name = Employee.query.filter_by(name=user.username).first()
    if emp_by_name:
        print(f"   3. ✓ Found employee: {emp_by_name.name}")
    else:
        print(f"   3. ✗ NOT FOUND (no employee named '{user.username}')")
    
    print(f"   4. Returns: Empty array []")
    print(f"   5. Frontend shows: 'No attendance records found' ❌")
    
    # Show what correct code would do
    print(f"\n✅ What Correct Code Should Do:")
    print(f"   1. User logs in as '{user.username}' (User ID: {user.id})")
    print(f"   2. Code searches: Employee.query.filter_by(user_id={user.id})")
    
    emp_by_id = Employee.query.filter_by(user_id=user.id).first()
    if emp_by_id:
        att_count = Attendance.query.filter_by(employee_id=emp_by_id.id).count()
        print(f"   3. ✓ Found employee: {emp_by_id.name} (ID: {emp_by_id.id})")
        print(f"   4. Query attendance: WHERE employee_id = {emp_by_id.id}")
        print(f"   5. Returns: {att_count} records")
        print(f"   6. Frontend shows: All {att_count} attendance records ✅")
    else:
        print(f"   3. ✗ NOT FOUND (user not linked to employee)")
        print(f"   4. Need to run: fix_employee_profiles.py")

def provide_solution():
    """Provide the exact solution based on findings"""
    print_section("💡 SOLUTION")
    
    # Recheck
    with open('app.py', 'r') as f:
        content = f.read()
    
    has_code_bug = 'filter_by(name=user.username)' in content
    
    if has_code_bug:
        print("You need to fix THE CODE BUG first:")
        print("\nOption 1: Run automated fix")
        print("   python fix_all_employee_endpoints.py")
        print("\nOption 2: Manual fix")
        print("   Edit app.py:")
        print("   • Line ~2574 (my-payslips)")
        print("   • Line ~2612 (my-attendance)")
        print("   Change: filter_by(name=user.username)")
        print("   To: filter_by(user_id=user.id)")
    else:
        print("✅ Code appears fixed!")
    
    # Check user links
    unlinked = User.query.outerjoin(Employee, User.id == Employee.user_id).filter(Employee.id == None).count()
    
    if unlinked > 0:
        print(f"\nYou also need to fix USER LINKS ({unlinked} users):")
        print("   python fix_employee_profiles.py")
    else:
        print("\n✅ All users are linked to employees")
    
    print("\nAfter fixing:")
    print("   1. Restart backend: python app.py")
    print("   2. Clear browser cache")
    print("   3. Test: Login as 'fnjoroge' and check attendance")

def main():
    print_header("HRMS Real-Time Diagnostic")
    print("Checking why attendance and payslips are not working...\n")
    
    with app.app_context():
        try:
            code_ok = check_code_bugs()
            links_ok = check_user_links()
            test_attendance_query()
            check_data_availability()
            show_exact_problem()
            provide_solution()
            
            print_header("DIAGNOSTIC COMPLETE")
            
            if not code_ok:
                print("🔴 PRIMARY ISSUE: Code bug in app.py")
                print("   ALL employees affected - nobody can see attendance/payslips")
                print("\n   FIX: Run 'python fix_all_employee_endpoints.py'")
            elif not links_ok:
                print("⚠️  ISSUE: Some users not linked to employees")
                print("   SOME employees affected")
                print("\n   FIX: Run 'python fix_employee_profiles.py'")
            else:
                print("✅ System looks correct!")
                print("   If still not working, check:")
                print("   • Backend server is running")
                print("   • Frontend API URL is correct")
                print("   • Browser cache cleared")
                print("   • JWT token is valid")
            
        except Exception as e:
            print(f"\n❌ ERROR: {str(e)}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    main()
