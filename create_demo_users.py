"""
Demo User Creation Script for HRMS System
Creates all 4 demo accounts (Admin, Manager, HR Officer, Employee)
"""
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(__file__))

from flask import Flask
from database import db
from models import User

# Create minimal Flask app for database access
app = Flask(__name__)
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
db_path = os.path.join(BASE_DIR, "instance", "hrms.db")

app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{db_path}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

def create_all_demo_users():
    """Create all demo user accounts for testing"""
    
    with app.app_context():
        demo_accounts = [
            {
                "username": "admin",
                "password": "admin123",
                "role": "Admin"
            },
            {
                "username": "manager",
                "password": "manager123",
                "role": "Manager"
            },
            {
                "username": "hr_officer",
                "password": "OfficerPass123",
                "role": "HR Officer"
            },
            {
                "username": "employee",
                "password": "employee123",
                "role": "Employee"
            }
        ]
        
        created_count = 0
        updated_count = 0
        
        for account in demo_accounts:
            # Check if user already exists
            existing_user = User.query.filter_by(username=account["username"]).first()
            
            if existing_user:
                # Update password for existing user
                existing_user.set_password(account["password"])
                existing_user.role = account["role"]
                print(f"✅ Updated: {account['username']} (Role: {account['role']})")
                updated_count += 1
            else:
                # Create new user
                new_user = User(
                    username=account["username"],
                    role=account["role"]
                )
                new_user.set_password(account["password"])
                db.session.add(new_user)
                print(f"✨ Created: {account['username']} (Role: {account['role']})")
                created_count += 1
        
        # Commit all changes
        db.session.commit()
        
        print("\n" + "="*50)
        print("🎉 All Demo Users Setup Complete!")
        print("="*50)
        print(f"Created: {created_count} new users")
        print(f"Updated: {updated_count} existing users")
        print("\n📋 Available Accounts:")
        print("-" * 50)
        print("1. Admin Account:")
        print("   Username: admin")
        print("   Password: admin123")
        print("   Role: Admin")
        print("   Access: Full system access")
        print()
        print("2. Manager Account:")
        print("   Username: manager")
        print("   Password: manager123")
        print("   Role: Manager")
        print("   Access: All operations except Audit Trail")
        print()
        print("3. HR Officer Account:")
        print("   Username: hr_officer")
        print("   Password: OfficerPass123")
        print("   Role: HR Officer")
        print("   Access: Employee management (cannot delete)")
        print()
        print("4. Employee Account:")
        print("   Username: employee")
        print("   Password: employee123")
        print("   Role: Employee")
        print("   Access: View dashboard only")
        print("-" * 50)
        print("\n💡 Usage:")
        print("   - Use 'admin' to submit payroll")
        print("   - Use 'manager' to approve payroll (Separation of Duties)")
        print("   - Use 'hr_officer' to test limited employee management")
        print("   - Use 'employee' for regular employee view")
        print("="*50)

if __name__ == "__main__":
    print("\n🚀 Creating All Demo User Accounts...")
    print("="*50)
    create_all_demo_users()