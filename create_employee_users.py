"""
Create User Accounts for Employees
This script creates user accounts for all employees who don't have one yet.
"""

from app import app, db
from models import User, Employee
from werkzeug.security import generate_password_hash

def create_user_accounts_for_employees():
    """Create user accounts for employees without accounts"""
    
    with app.app_context():
        # Find employees without user accounts
        employees_without_accounts = Employee.query.filter_by(user_id=None).all()
        
        print(f"\n{'='*60}")
        print(f"CREATING USER ACCOUNTS FOR EMPLOYEES")
        print(f"{'='*60}")
        print(f"\nFound {len(employees_without_accounts)} employees without user accounts\n")
        
        if len(employees_without_accounts) == 0:
            print("✅ All employees already have user accounts!")
            return
        
        created_count = 0
        failed_count = 0
        
        for employee in employees_without_accounts:
            try:
                # Generate username from employee name
                # Example: "John Doe" -> "jdoe"
                name_parts = employee.name.lower().split()
                if len(name_parts) >= 2:
                    # First letter of first name + last name
                    username = name_parts[0][0] + name_parts[-1]
                else:
                    # Just use the name
                    username = name_parts[0]
                
                # Remove spaces and special characters
                username = ''.join(c for c in username if c.isalnum())
                
                # Check if username already exists, add number if needed
                base_username = username
                counter = 1
                while User.query.filter_by(username=username).first():
                    username = f"{base_username}{counter}"
                    counter += 1
                
                # Generate simple password: name + 123
                # Example: "jdoe123"
                password = f"{username}123"
                
                # Create user account
                new_user = User(
                    username=username,
                    role='Employee',
                    email=employee.email,
                    phone=employee.phone_number,
                    is_active=True if employee.active else False
                )
                new_user.set_password(password)
                
                # Save user
                db.session.add(new_user)
                db.session.flush()  # Get the user ID
                
                # Link employee to user
                employee.user_id = new_user.id
                
                db.session.commit()
                
                print(f"✅ Created account for: {employee.name}")
                print(f"   Username: {username}")
                print(f"   Password: {password}")
                print(f"   Email: {employee.email or 'N/A'}")
                print()
                
                created_count += 1
                
            except Exception as e:
                db.session.rollback()
                print(f"❌ Failed to create account for {employee.name}: {str(e)}")
                failed_count += 1
        
        print(f"\n{'='*60}")
        print(f"SUMMARY")
        print(f"{'='*60}")
        print(f"✅ Successfully created: {created_count} accounts")
        if failed_count > 0:
            print(f"❌ Failed: {failed_count} accounts")
        print(f"\n⚠️  IMPORTANT: Save these credentials!")
        print(f"    All passwords follow pattern: username + '123'")
        print(f"    Example: jdoe123, msmith123, etc.")
        print(f"\n{'='*60}\n")


def export_credentials_to_file():
    """Export all employee credentials to a CSV file"""
    
    with app.app_context():
        import csv
        from datetime import datetime
        
        # Get all employees with user accounts
        employees = Employee.query.filter(Employee.user_id.isnot(None)).all()
        
        filename = f"employee_credentials_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
        with open(filename, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['Employee ID', 'Name', 'Department', 'Username', 'Email', 'Default Password'])
            
            for emp in employees:
                user = User.query.get(emp.user_id)
                if user:
                    # Default password is username + 123
                    default_password = f"{user.username}123"
                    writer.writerow([
                        emp.id,
                        emp.name,
                        emp.department,
                        user.username,
                        emp.email or 'N/A',
                        default_password
                    ])
        
        print(f"✅ Credentials exported to: {filename}")
        return filename


def show_employees_without_accounts():
    """Show which employees don't have user accounts"""
    
    with app.app_context():
        employees_without_accounts = Employee.query.filter_by(user_id=None).all()
        
        print(f"\n{'='*60}")
        print(f"EMPLOYEES WITHOUT USER ACCOUNTS")
        print(f"{'='*60}\n")
        
        if len(employees_without_accounts) == 0:
            print("✅ All employees have user accounts!\n")
        else:
            print(f"Found {len(employees_without_accounts)} employees without accounts:\n")
            
            for emp in employees_without_accounts:
                print(f"  ID: {emp.id:3d} | {emp.name:30s} | {emp.department:20s} | {emp.email or 'No email'}")
            
            print(f"\n{'='*60}\n")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "show":
            show_employees_without_accounts()
        elif command == "create":
            create_user_accounts_for_employees()
        elif command == "export":
            export_credentials_to_file()
        else:
            print("Unknown command. Use: show, create, or export")
    else:
        print("""
┌─────────────────────────────────────────────────────────┐
│   CREATE USER ACCOUNTS FOR EMPLOYEES                    │
└─────────────────────────────────────────────────────────┘

Usage:
  python create_employee_users.py show     - Show employees without accounts
  python create_employee_users.py create   - Create accounts for all employees
  python create_employee_users.py export   - Export all credentials to CSV

What this does:
  1. Finds employees without user accounts
  2. Creates username from their name (e.g., "John Doe" -> "jdoe")
  3. Sets password as: username + "123" (e.g., "jdoe123")
  4. Links the user account to the employee profile
  5. Sets role as "Employee"

Example:
  Employee: John Doe
  Username: jdoe
  Password: jdoe123
  Role: Employee

⚠️  IMPORTANT:
  - Make sure to save the credentials that are printed!
  - Users can change their password after first login
  - Use 'export' command to save all credentials to CSV file
        """)
