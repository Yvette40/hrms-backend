"""
Add HR Officer User Account to HRMS System
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

def create_hr_officer():
    """Create HR Officer user account"""
    
    with app.app_context():
        # Check if HR Officer already exists
        existing_user = User.query.filter_by(username="hr_officer").first()
        
        if existing_user:
            # Update existing user
            existing_user.set_password("OfficerPass123")
            existing_user.role = "HR Officer"
            db.session.commit()
            print("✅ Updated: hr_officer (Role: HR Officer)")
            print("   Password reset to: OfficerPass123")
        else:
            # Create new user
            new_user = User(
                username="hr_officer",
                role="HR Officer"
            )
            new_user.set_password("OfficerPass123")
            db.session.add(new_user)
            db.session.commit()
            print("✨ Created: hr_officer (Role: HR Officer)")
            print("   Password: OfficerPass123")
        
        print("\n" + "="*50)
        print("🎉 HR Officer Account Ready!")
        print("="*50)
        print("\n📋 Login Credentials:")
        print("-" * 50)
        print("Username: hr_officer")
        print("Password: OfficerPass123")
        print("Role: HR Officer")
        print("-" * 50)
        print("\n💡 Permissions:")
        print("   ✅ View employees")
        print("   ✅ Add employees")
        print("   ✅ Edit employees")
        print("   ❌ Delete employees (Admin/Manager only)")
        print("="*50)

if __name__ == "__main__":
    print("\n🚀 Creating HR Officer Account...")
    print("="*50)
    create_hr_officer()
