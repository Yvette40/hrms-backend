import sys
import os
import json
from datetime import datetime, timedelta
import random

# Import from your existing app
# Note: Adjust these imports based on your actual project structure
try:
    from app import app, db
    from models import User, Employee, Attendance
except ImportError:
    print("❌ Error: Cannot import app modules.")
    print("Make sure this script is in your project directory with app.py and models.py")
    sys.exit(1)


def load_employee_data():
    """Load the generated employee data from JSON"""
    try:
        with open('employees_data.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print("❌ Error: employees_data.json not found!")
        print("Please run: python enhanced_seed_data.py first")
        sys.exit(1)


def seed_system_users():
    """Create default users for system roles (Admin, HR, Manager)"""
    users_data = [
        {
            "username": "admin",
            "password": "admin123",
            "role": "Admin",
            "email": "admin@glimmer.com",
            "phone": "+254700000001"
        },
        {
            "username": "hr_officer",
            "password": "OfficerPass123",
            "role": "HR Officer",
            "email": "hr@glimmer.com",
            "phone": "+254700000002"
        },
        {
            "username": "dept_manager",
            "password": "DeptPass123",
            "role": "Department Manager",
            "email": "manager@glimmer.com",
            "phone": "+254700000003"
        },
    ]
    
    print("\n🔐 Creating System Users...")
    created = 0
    
    for user_data in users_data:
        existing = User.query.filter_by(username=user_data["username"]).first()
        
        if not existing:
            user = User(
                username=user_data["username"],
                role=user_data["role"],
                email=user_data.get("email"),
                phone=user_data.get("phone")
            )
            user.set_password(user_data["password"])
            db.session.add(user)
            print(f"   ✅ Created user: {user_data['username']} ({user_data['role']})")
            created += 1
        else:
            print(f"   ⏭️  User already exists: {user_data['username']}")
    
    db.session.commit()
    print(f"✅ System users complete! ({created} new users created)")
    return created


def seed_employees():
    """Create employees with individual user accounts from generated data"""
    print("\n👥 Creating Employees with User Accounts...")
    
    employees_data = load_employee_data()
    created = 0
    skipped = 0
    
    for emp_data in employees_data:
        # Check if employee already exists
        existing_emp = Employee.query.filter_by(national_id=emp_data["national_id"]).first()
        
        if existing_emp:
            print(f"   ⏭️  Employee already exists: {emp_data['name']}")
            skipped += 1
            continue
        
        # Create user account first
        user = User.query.filter_by(username=emp_data["username"]).first()
        
        if not user:
            user = User(
                username=emp_data["username"],
                role="Employee",
                email=emp_data.get("email"),
                phone=emp_data.get("phone_number")
            )
            user.set_password(emp_data["password"])
            db.session.add(user)
            db.session.flush()  # Get the user ID
        
        # Create employee record linked to user
        employee = Employee(
            name=emp_data["name"],
            national_id=emp_data["national_id"],
            base_salary=emp_data["base_salary"],
            phone_number=emp_data.get("phone_number"),
            email=emp_data.get("email"),
            department=emp_data.get("department", "General"),
            position=emp_data.get("position", "Employee"),
            user_id=user.id
        )
        
        # Set join_date if provided
        if "join_date" in emp_data:
            employee.join_date = datetime.fromisoformat(emp_data["join_date"]).date()
        
        db.session.add(employee)
        
        if created % 10 == 0 and created > 0:
            print(f"   📊 Created {created} employees so far...")
        
        created += 1
    
    db.session.commit()
    print(f"✅ Employees complete! ({created} new employees, {skipped} skipped)")
    return created


def seed_attendance():
    """Create sample attendance records for the last 30 days"""
    print("\n📅 Creating Attendance Records...")
    
    employees = Employee.query.all()
    if not employees:
        print("   ⚠️  No employees found. Skipping attendance seeding.")
        return 0
    
    # Create attendance for the last 30 days
    today = datetime.now().date()
    attendance_count = 0
    
    for employee in employees:
        for days_ago in range(30):
            date = today - timedelta(days=days_ago)
            
            # Skip weekends
            if date.weekday() >= 5:  # 5=Saturday, 6=Sunday
                continue
            
            # Check if attendance already exists
            existing = Attendance.query.filter_by(
                employee_id=employee.id,
                date=date
            ).first()
            
            if not existing:
                # 92% chance of being present, 8% chance of being absent
                status = "Present" if random.random() < 0.92 else "Absent"
                
                attendance = Attendance(
                    employee_id=employee.id,
                    date=date,
                    status=status
                )
                db.session.add(attendance)
                attendance_count += 1
        
        if attendance_count % 100 == 0 and attendance_count > 0:
            print(f"   📊 Created {attendance_count} attendance records so far...")
    
    db.session.commit()
    print(f"✅ Attendance complete! ({attendance_count} records created)")
    return attendance_count


def print_summary():
    """Print a summary of the database contents"""
    user_count = User.query.count()
    employee_count = Employee.query.count()
    attendance_count = Attendance.query.count()
    
    # Get department breakdown
    departments = db.session.query(
        Employee.department,
        db.func.count(Employee.id)
    ).group_by(Employee.department).all()
    
    print("\n" + "=" * 80)
    print("📊 DATABASE SUMMARY")
    print("=" * 80)
    
    print(f"\n📈 Record Counts:")
    print(f"   • Total Users: {user_count}")
    print(f"     - System Users: 3 (Admin, HR Officer, Department Manager)")
    print(f"     - Employee Users: {user_count - 3}")
    print(f"   • Total Employees: {employee_count}")
    print(f"   • Attendance Records: {attendance_count}")
    
    print(f"\n🏢 Department Breakdown:")
    for dept, count in sorted(departments):
        print(f"   • {dept:25} {count:3} employees")
    
    print(f"\n🔐 Sample Employee Logins:")
    sample_employees = Employee.query.filter(Employee.user_id.isnot(None)).limit(5).all()
    for emp in sample_employees:
        print(f"   • Username: {emp.user.username:15} | Password: password123 | {emp.name:25} ({emp.department})")
    
    print(f"\n🔐 System User Logins:")
    print(f"   • Username: admin         | Password: admin123     | Admin")
    print(f"   • Username: hr_officer    | Password: OfficerPass123   | HR Officer")
    print(f"   • Username: dept_manager  | Password: DeptPass123      | Department Manager")
    
    print("\n" + "=" * 80)


def seed_all():
    """Run all seeding functions"""
    print("=" * 80)
    print("🌱 STARTING COMPREHENSIVE DATABASE SEEDING")
    print("=" * 80)
    
    with app.app_context():
        try:
            # Step 1: System Users
            system_users_created = seed_system_users()
            
            # Step 2: Employees
            employees_created = seed_employees()
            
            # Step 3: Attendance
            attendance_created = seed_attendance()
            
            # Print summary
            print_summary()
            
            print("\n" + "=" * 80)
            print("✅ DATABASE SEEDING COMPLETED SUCCESSFULLY!")
            print("=" * 80)
            
            print(f"\n📝 Summary:")
            print(f"   • System users created: {system_users_created}")
            print(f"   • Employees created: {employees_created}")
            print(f"   • Attendance records created: {attendance_created}")
            
            print("\n💡 Tips:")
            print("   • All employee passwords are: password123")
            print("   • System user passwords are shown in the summary above")
            print("   • Usernames follow pattern: [first_initial][surname]")
            print("   • You can now log in and test the system!")
            
            print("\n" + "=" * 80)
            
        except Exception as e:
            print(f"\n❌ Error during seeding: {e}")
            import traceback
            traceback.print_exc()
            db.session.rollback()


if __name__ == "__main__":
    print("\n⚠️  WARNING: This script will add new data to your database.")
    print("Existing records will NOT be deleted, but duplicates will be skipped.\n")
    
    response = input("Continue? (yes/no): ").strip().lower()
    
    if response in ['yes', 'y']:
        seed_all()
    else:
        print("\n❌ Seeding cancelled by user.")
