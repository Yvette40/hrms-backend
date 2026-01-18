"""
Create 5 Test Employee Profiles
================================
This script creates 5 employee users with complete profile data for testing.

Run this script: python create_test_employees.py
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from app import app, db
from models import User, Employee
from datetime import datetime, date
from werkzeug.security import generate_password_hash

def create_test_employees():
    """Create 5 test employees with user accounts"""
    
    with app.app_context():
        print("🚀 Creating 5 test employee profiles...\n")
        
        # Test employee data
        test_employees = [
            {
                'username': 'jmwangi',
                'password': 'password123',
                'name': 'John Mwangi',
                'national_id': '12345678',
                'email': 'jmwangi@company.com',
                'phone': '+254712345678',
                'department': 'Engineering',
                'position': 'Software Engineer',
                'base_salary': 80000.00,
                'address': 'Kilimani, Nairobi',
                'emergency_contact': '+254722111222',
                'emergency_name': 'Jane Mwangi',
                'join_date': date(2023, 1, 15)
            },
            {
                'username': 'akinyi',
                'password': 'password123',
                'name': 'Alice Akinyi',
                'national_id': '23456789',
                'email': 'akinyi@company.com',
                'phone': '+254723456789',
                'department': 'Human Resources',
                'position': 'HR Specialist',
                'base_salary': 65000.00,
                'address': 'Westlands, Nairobi',
                'emergency_contact': '+254733222333',
                'emergency_name': 'Peter Akinyi',
                'join_date': date(2022, 6, 1)
            },
            {
                'username': 'koech',
                'password': 'password123',
                'name': 'David Koech',
                'national_id': '34567890',
                'email': 'koech@company.com',
                'phone': '+254734567890',
                'department': 'Finance',
                'position': 'Accountant',
                'base_salary': 70000.00,
                'address': 'Parklands, Nairobi',
                'emergency_contact': '+254744333444',
                'emergency_name': 'Mary Koech',
                'join_date': date(2023, 3, 20)
            },
            {
                'username': 'wanjiru',
                'password': 'password123',
                'name': 'Grace Wanjiru',
                'national_id': '45678901',
                'email': 'wanjiru@company.com',
                'phone': '+254745678901',
                'department': 'Marketing',
                'position': 'Marketing Manager',
                'base_salary': 90000.00,
                'address': 'Karen, Nairobi',
                'emergency_contact': '+254755444555',
                'emergency_name': 'Joseph Wanjiru',
                'join_date': date(2021, 9, 10)
            },
            {
                'username': 'omondi',
                'password': 'password123',
                'name': 'James Omondi',
                'national_id': '56789012',
                'email': 'omondi@company.com',
                'phone': '+254756789012',
                'department': 'Operations',
                'position': 'Operations Coordinator',
                'base_salary': 60000.00,
                'address': 'South B, Nairobi',
                'emergency_contact': '+254766555666',
                'emergency_name': 'Susan Omondi',
                'join_date': date(2024, 1, 5)
            }
        ]
        
        created_count = 0
        
        for emp_data in test_employees:
            try:
                # Check if user already exists
                existing_user = User.query.filter_by(username=emp_data['username']).first()
                if existing_user:
                    print(f"⚠️  User '{emp_data['username']}' already exists. Skipping...")
                    continue
                
                # Check if employee already exists
                existing_employee = Employee.query.filter_by(national_id=emp_data['national_id']).first()
                if existing_employee:
                    print(f"⚠️  Employee with ID '{emp_data['national_id']}' already exists. Skipping...")
                    continue
                
                # Create User account
                user = User(
                    username=emp_data['username'],
                    role='employee',
                    email=emp_data['email'],
                    phone=emp_data['phone'],
                    is_active=True
                )
                user.set_password(emp_data['password'])
                db.session.add(user)
                db.session.flush()  # Get the user ID
                
                # Create Employee profile
                employee = Employee(
                    name=emp_data['name'],
                    national_id=emp_data['national_id'],
                    base_salary=emp_data['base_salary'],
                    department=emp_data['department'],
                    position=emp_data['position'],
                    email=emp_data['email'],
                    phone_number=emp_data['phone'],
                    join_date=emp_data['join_date'],
                    address=emp_data['address'],
                    emergency_contact=emp_data['emergency_contact'],
                    emergency_name=emp_data['emergency_name'],
                    leave_balance=21,
                    active=True,
                    user_id=user.id  # Link to user account
                )
                db.session.add(employee)
                db.session.commit()
                
                created_count += 1
                print(f"✅ Created: {emp_data['name']} (username: {emp_data['username']})")
                
            except Exception as e:
                db.session.rollback()
                print(f"❌ Error creating {emp_data['name']}: {str(e)}")
        
        print(f"\n{'='*60}")
        print(f"✨ Successfully created {created_count} test employee(s)!")
        print(f"{'='*60}\n")
        
        # Print login credentials
        if created_count > 0:
            print("🔐 TEST LOGIN CREDENTIALS:")
            print("-" * 60)
            for emp in test_employees:
                user_exists = User.query.filter_by(username=emp['username']).first()
                if user_exists:
                    print(f"Name: {emp['name']}")
                    print(f"Username: {emp['username']}")
                    print(f"Password: {emp['password']}")
                    print(f"Department: {emp['department']}")
                    print(f"Position: {emp['position']}")
                    print("-" * 60)
            
            print("\n📝 INSTRUCTIONS:")
            print("1. Go to http://localhost:3000/employee-login")
            print("2. Login with any of the usernames above")
            print("3. Password for all: password123")
            print("4. After login, go to Profile to see their data")
            print("\n✨ Happy testing!\n")

if __name__ == '__main__':
    create_test_employees()
