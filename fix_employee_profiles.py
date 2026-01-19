#!/usr/bin/env python3
"""
HRMS Employee Profile Fix Script
=================================
This script fixes the issue where users cannot view their profile because
they are not linked to employee records in the database.

Issues Fixed:
1. Links user 'jmwangi' (ID: 89) to employee 'John Mwangi'
2. Creates employee profiles for system users (admin, hr_officer, etc.)
3. Verifies all user-employee links

Usage:
    python fix_employee_profiles.py
"""

from datetime import date
import sys
import os

# Add the current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from models import User, Employee

def print_header(text):
    """Print a formatted header"""
    print(f"\n{'='*70}")
    print(f"  {text}")
    print(f"{'='*70}\n")

def print_step(step_num, text):
    """Print a step number and description"""
    print(f"\n[STEP {step_num}] {text}")
    print("-" * 70)

def fix_jmwangi_link():
    """Fix the link between user jmwangi and employee John Mwangi"""
    print_step(1, "Fixing jmwangi User Link")
    
    jmwangi_user = User.query.get(89)
    john_employee = Employee.query.filter_by(email='john.mwangi@glimmer.com').first()
    
    if not jmwangi_user:
        print("❌ User 'jmwangi' (ID: 89) not found in database")
        return False
    
    if not john_employee:
        print("❌ Employee 'John Mwangi' not found in database")
        return False
    
    # Check current link status
    current_user_id = john_employee.user_id
    print(f"📊 Current Status:")
    print(f"   User: {jmwangi_user.username} (ID: {jmwangi_user.id})")
    print(f"   Employee: {john_employee.name} (ID: {john_employee.id})")
    print(f"   Current user_id in employee: {current_user_id}")
    
    if current_user_id == jmwangi_user.id:
        print("✅ Already linked correctly!")
        return True
    
    # Fix the link
    john_employee.user_id = jmwangi_user.id
    try:
        db.session.commit()
        print(f"✅ Successfully linked user 'jmwangi' → employee 'John Mwangi'")
        return True
    except Exception as e:
        db.session.rollback()
        print(f"❌ Error linking: {str(e)}")
        return False

def create_system_employee_profiles():
    """Create employee profiles for system users"""
    print_step(2, "Creating System Employee Profiles")
    
    system_accounts = [
        {
            'user_id': 1,
            'username': 'admin',
            'name': 'System Administrator',
            'national_id': 'ADMIN001',
            'department': 'Administration',
            'position': 'System Administrator',
            'base_salary': 120000.00
        },
        {
            'user_id': 2,
            'username': 'hr_officer',
            'name': 'HR Officer',
            'national_id': 'HR001',
            'department': 'Human Resources',
            'position': 'HR Officer',
            'base_salary': 90000.00
        },
        {
            'user_id': 3,
            'username': 'dept_manager',
            'name': 'Department Manager',
            'national_id': 'MGR001',
            'department': 'Management',
            'position': 'Department Manager',
            'base_salary': 100000.00
        },
        {
            'user_id': 4,
            'username': 'employee',
            'name': 'General Employee',
            'national_id': 'EMP000',
            'department': 'General',
            'position': 'Employee',
            'base_salary': 50000.00
        }
    ]
    
    created_count = 0
    skipped_count = 0
    
    for account in system_accounts:
        user = User.query.get(account['user_id'])
        
        if not user:
            print(f"⚠️  User '{account['username']}' (ID: {account['user_id']}) not found - skipping")
            continue
        
        # Check if employee profile already exists
        existing_emp = Employee.query.filter_by(user_id=account['user_id']).first()
        
        if existing_emp:
            print(f"✓  User '{account['username']}' already has employee profile (ID: {existing_emp.id})")
            skipped_count += 1
            continue
        
        # Create new employee profile
        new_employee = Employee(
            name=account['name'],
            national_id=account['national_id'],
            department=account['department'],
            position=account['position'],
            email=user.email or f"{account['username']}@company.com",
            phone_number=user.phone or '+254700000000',
            base_salary=account['base_salary'],
            join_date=date.today(),
            user_id=account['user_id'],
            active=True,
            leave_balance=21
        )
        
        try:
            db.session.add(new_employee)
            db.session.commit()
            print(f"✅ Created employee profile for '{account['username']}' (Employee ID: {new_employee.id})")
            created_count += 1
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error creating profile for '{account['username']}': {str(e)}")
    
    print(f"\n📊 Summary: Created {created_count}, Skipped {skipped_count}")
    return created_count > 0

def verify_all_links():
    """Verify all user-employee links"""
    print_step(3, "Verifying All User-Employee Links")
    
    all_users = User.query.all()
    users_without_employees = []
    users_with_employees = []
    
    for user in all_users:
        employee = Employee.query.filter_by(user_id=user.id).first()
        if employee:
            users_with_employees.append((user, employee))
        else:
            users_without_employees.append(user)
    
    print(f"📊 Total Users: {len(all_users)}")
    print(f"✅ Users with Employee Profile: {len(users_with_employees)}")
    print(f"❌ Users WITHOUT Employee Profile: {len(users_without_employees)}")
    
    if users_without_employees:
        print(f"\n⚠️  The following {len(users_without_employees)} user(s) still have no employee profile:")
        for user in users_without_employees:
            print(f"   - {user.username} (ID: {user.id}, Role: {user.role})")
        return False
    else:
        print("\n✅ SUCCESS! All users now have employee profiles!")
        return True

def show_sample_profiles():
    """Show sample of linked profiles"""
    print_step(4, "Sample Linked Profiles")
    
    # Show the fixed users
    target_users = ['admin', 'hr_officer', 'dept_manager', 'employee', 'jmwangi']
    
    for username in target_users:
        user = User.query.filter_by(username=username).first()
        if not user:
            continue
        
        employee = Employee.query.filter_by(user_id=user.id).first()
        if employee:
            print(f"✅ {username} (User ID: {user.id})")
            print(f"   → Employee: {employee.name} (ID: {employee.id})")
            print(f"   → Department: {employee.department}, Position: {employee.position}")
        else:
            print(f"❌ {username} (User ID: {user.id}) - NO EMPLOYEE PROFILE")
        print()

def main():
    """Main execution function"""
    print_header("HRMS Employee Profile Fix Script")
    print("This script will fix user-employee linking issues in the database.")
    print("\nIssues to be fixed:")
    print("  1. Link user 'jmwangi' to employee 'John Mwangi'")
    print("  2. Create employee profiles for system users")
    print("  3. Verify all links are correct")
    
    response = input("\nDo you want to proceed? (yes/no): ").strip().lower()
    if response not in ['yes', 'y']:
        print("\n❌ Operation cancelled by user")
        return
    
    with app.app_context():
        try:
            # Step 1: Fix jmwangi link
            fix_jmwangi_link()
            
            # Step 2: Create system employee profiles
            create_system_employee_profiles()
            
            # Step 3: Verify all links
            all_good = verify_all_links()
            
            # Step 4: Show sample profiles
            show_sample_profiles()
            
            # Final summary
            print_header("FIX COMPLETE")
            if all_good:
                print("✅ All user-employee links have been successfully fixed!")
                print("\n📝 Next Steps:")
                print("   1. Test the employee profile page with different users")
                print("   2. Verify that all data displays correctly")
                print("   3. Test profile editing functionality")
            else:
                print("⚠️  Some users still don't have employee profiles.")
                print("   Review the output above for details.")
            
        except Exception as e:
            print(f"\n❌ CRITICAL ERROR: {str(e)}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    main()
