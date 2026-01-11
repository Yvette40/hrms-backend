"""
DOCUMENT-ALIGNED Demo User Creation Script for HRMS System
Creates 4 user accounts matching the Use Case Diagram (Section 3.7.1)

Actors from Document:
1. Admin - System control, user management, role verification
2. HR Officer - Employee records, attendance, payroll processing, leave approvals, audit trails
3. Department Manager - View department employees, monitor attendance, departmental reports
4. Employee - View profile, attendance, payslips, submit leave requests
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

def create_document_aligned_users():
    """Create user accounts matching document specification"""
    
    with app.app_context():
        # EXACTLY as specified in Use Case Diagram (Figure 3.7.1)
        demo_accounts = [
            {
                "username": "admin",
                "password": "admin123",
                "role": "Admin",
                "description": "System control, user management, role verification"
            },
            {
                "username": "hr_officer",
                "password": "OfficerPass123",
                "role": "HR Officer",
                "description": "Employee records, attendance, payroll processing, leave approvals, audit trails"
            },
            {
                "username": "dept_manager",
                "password": "DeptPass123",
                "role": "Department Manager",
                "description": "View department employees, monitor attendance, departmental reports"
            },
            {
                "username": "employee",
                "password": "employee123",
                "role": "Employee",
                "description": "View profile, attendance, payslips, submit leave requests"
            }
        ]
        
        created_count = 0
        updated_count = 0
        
        print("\n" + "="*70)
        print("🎓 CREATING USERS - ALIGNED WITH DOCUMENT SPECIFICATION")
        print("   (Use Case Diagram - Section 3.7.1)")
        print("="*70 + "\n")
        
        for account in demo_accounts:
            # Check if user already exists
            existing_user = User.query.filter_by(username=account["username"]).first()
            
            if existing_user:
                # Update password and role for existing user
                existing_user.set_password(account["password"])
                existing_user.role = account["role"]
                print(f"✅ Updated: {account['username']:<15} (Role: {account['role']})")
                updated_count += 1
            else:
                # Create new user
                new_user = User(
                    username=account["username"],
                    role=account["role"]
                )
                new_user.set_password(account["password"])
                db.session.add(new_user)
                print(f"✨ Created: {account['username']:<15} (Role: {account['role']})")
                created_count += 1
        
        # Commit all changes
        db.session.commit()
        
        print("\n" + "="*70)
        print("🎉 DOCUMENT-ALIGNED USER ACCOUNTS READY!")
        print("="*70)
        print(f"Created: {created_count} new users")
        print(f"Updated: {updated_count} existing users")
        
        print("\n" + "="*70)
        print("📋 AVAILABLE ACCOUNTS (Per Use Case Diagram)")
        print("="*70 + "\n")
        
        for idx, account in enumerate(demo_accounts, 1):
            print(f"{idx}. {account['role']} Account:")
            print(f"   Username: {account['username']}")
            print(f"   Password: {account['password']}")
            print(f"   Responsibilities: {account['description']}")
            print()
        
        print("="*70)
        print("💡 USAGE GUIDE:")
        print("="*70)
        print("✅ Admin:")
        print("   - Manages user accounts")
        print("   - Verifies roles")
        print("   - Approves payroll (Separation of Duties)")
        print()
        print("✅ HR Officer:")
        print("   - Processes payroll")
        print("   - Manages employee records")
        print("   - Tracks attendance")
        print("   - Approves leave requests")
        print()
        print("✅ Department Manager:")
        print("   - Views department employees")
        print("   - Monitors department attendance")
        print("   - Accesses departmental reports")
        print()
        print("✅ Employee:")
        print("   - Views personal profile")
        print("   - Checks attendance")
        print("   - Views payslips")
        print("   - Submits leave requests")
        print("="*70)
        
        print("\n" + "="*70)
        print("🔒 SEPARATION OF DUTIES WORKFLOW:")
        print("="*70)
        print("   HR Officer submits payroll → Admin approves payroll")
        print("   (This prevents fraud as per document Section 2.2.1)")
        print("="*70 + "\n")

if __name__ == "__main__":
    create_document_aligned_users()
