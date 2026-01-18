#!/usr/bin/env python3
"""
Attendance Diagnostic Tool
Checks why attendance data isn't showing for employees
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database import db
from app import app
from models import Employee, Attendance, User
from datetime import date, timedelta

print("🔍 ATTENDANCE DIAGNOSTIC TOOL")
print("="*60)

with app.app_context():
    # Check total attendance records
    total_attendance = Attendance.query.count()
    print(f"\n📊 Total Attendance Records: {total_attendance}")
    
    if total_attendance == 0:
        print("❌ No attendance records found in database!")
        print("💡 Run: python quick_generate_attendance.py")
        sys.exit(1)
    
    # Check employees
    total_employees = Employee.query.count()
    active_employees = Employee.query.filter_by(active=True).count()
    print(f"👥 Total Employees: {total_employees}")
    print(f"✅ Active Employees: {active_employees}")
    
    # Check users with employee profiles
    users_with_employees = User.query.join(
        Employee, User.id == Employee.user_id
    ).count()
    print(f"🔗 Users linked to Employees: {users_with_employees}")
    
    print("\n" + "="*60)
    print("📋 DETAILED EMPLOYEE ATTENDANCE CHECK")
    print("="*60)
    
    # Get all users
    users = User.query.all()
    
    for user in users[:20]:  # Check first 20 users
        # Find linked employee
        employee = Employee.query.filter_by(user_id=user.id).first()
        
        if employee:
            # Check attendance for this employee
            attendance_count = Attendance.query.filter_by(
                employee_id=employee.id
            ).count()
            
            if attendance_count > 0:
                # Get latest record
                latest = Attendance.query.filter_by(
                    employee_id=employee.id
                ).order_by(Attendance.date.desc()).first()
                
                # Get stats
                present = Attendance.query.filter_by(
                    employee_id=employee.id, 
                    status="Present"
                ).count()
                late = Attendance.query.filter_by(
                    employee_id=employee.id, 
                    status="Late"
                ).count()
                absent = Attendance.query.filter_by(
                    employee_id=employee.id, 
                    status="Absent"
                ).count()
                
                rate = (present / attendance_count * 100) if attendance_count > 0 else 0
                
                status_icon = "✅" if attendance_count > 0 else "❌"
                
                print(f"\n{status_icon} User: {user.username} (ID: {user.id})")
                print(f"   Employee: {employee.name} (ID: {employee.id})")
                print(f"   Records: {attendance_count}")
                print(f"   Latest: {latest.date if latest else 'N/A'}")
                print(f"   Present: {present} | Late: {late} | Absent: {absent}")
                print(f"   Rate: {rate:.1f}%")
            else:
                print(f"\n⚠️  User: {user.username} (ID: {user.id})")
                print(f"   Employee: {employee.name} (ID: {employee.id})")
                print(f"   ❌ NO ATTENDANCE RECORDS")
        else:
            print(f"\n⚠️  User: {user.username} (ID: {user.id})")
            print(f"   ❌ NO LINKED EMPLOYEE PROFILE")
    
    if len(users) > 20:
        print(f"\n... and {len(users) - 20} more users")
    
    # Check for orphaned attendance (employee not linked to user)
    print("\n" + "="*60)
    print("🔍 CHECKING FOR ORPHANED ATTENDANCE")
    print("="*60)
    
    employees_with_attendance = db.session.query(
        Employee.id
    ).join(Attendance).distinct().all()
    
    print(f"\n📊 Employees with attendance: {len(employees_with_attendance)}")
    
    for emp_id_tuple in employees_with_attendance[:10]:
        emp_id = emp_id_tuple[0]
        employee = Employee.query.get(emp_id)
        
        if employee:
            has_user = employee.user_id is not None
            user_icon = "✅" if has_user else "⚠️ "
            
            attendance_count = Attendance.query.filter_by(
                employee_id=emp_id
            ).count()
            
            print(f"{user_icon} Employee: {employee.name} (ID: {emp_id})")
            print(f"   User ID: {employee.user_id if has_user else 'NOT LINKED'}")
            print(f"   Attendance Records: {attendance_count}")
            
            if not has_user:
                print(f"   ⚠️  WARNING: This employee has attendance but no user account!")
    
    # Summary and recommendations
    print("\n" + "="*60)
    print("💡 RECOMMENDATIONS")
    print("="*60)
    
    employees_without_users = Employee.query.filter(
        Employee.user_id.is_(None)
    ).count()
    
    if employees_without_users > 0:
        print(f"\n⚠️  {employees_without_users} employees have no linked user accounts")
        print("   To fix: Link employees to user accounts in the database")
        print("   OR: Create user accounts for these employees")
    
    users_without_employees = User.query.filter(
        ~User.id.in_(
            db.session.query(Employee.user_id).filter(
                Employee.user_id.isnot(None)
            )
        )
    ).filter(User.role == 'employee').count()
    
    if users_without_employees > 0:
        print(f"\n⚠️  {users_without_employees} employee users have no linked employee profiles")
        print("   To fix: Link user accounts to employee records")
    
    # Test a specific user (if provided)
    print("\n" + "="*60)
    print("🧪 QUICK TEST")
    print("="*60)
    
    test_username = input("\nEnter username to check (or press Enter to skip): ").strip()
    
    if test_username:
        user = User.query.filter_by(username=test_username).first()
        
        if user:
            print(f"\n✅ User found: {user.username} (ID: {user.id})")
            employee = Employee.query.filter_by(user_id=user.id).first()
            
            if employee:
                print(f"✅ Employee found: {employee.name} (ID: {employee.id})")
                
                attendance = Attendance.query.filter_by(
                    employee_id=employee.id
                ).count()
                
                print(f"📊 Attendance records: {attendance}")
                
                if attendance > 0:
                    print("\n✅ This user SHOULD see attendance data!")
                    
                    # Show sample records
                    sample = Attendance.query.filter_by(
                        employee_id=employee.id
                    ).order_by(Attendance.date.desc()).limit(5).all()
                    
                    print("\n📋 Sample records:")
                    for rec in sample:
                        print(f"   {rec.date} - {rec.status}")
                else:
                    print("\n❌ This user has NO attendance records!")
                    print("💡 Generate attendance for this employee:")
                    print(f"   python generate_attendance_data.py --employee-id {employee.id} --days 90")
            else:
                print(f"❌ No employee profile linked to this user")
                print("💡 Link this user to an employee record in the database")
        else:
            print(f"\n❌ User '{test_username}' not found")

print("\n" + "="*60)
print("✅ Diagnostic complete!")
print("="*60)
