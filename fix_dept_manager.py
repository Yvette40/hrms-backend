from app import app, db
from models import User

with app.app_context():
    # Get or create dept_manager
    user = User.query.filter_by(username='dept_manager').first()
    
    if not user:
        print("Creating dept_manager user...")
        user = User(username='dept_manager', role='Department Manager')
    else:
        print("dept_manager user found! Resetting password...")
    
    # Set/reset password
    user.set_password('DeptPass123')
    user.is_active = True
    
    # Save
    if user.id is None:
        db.session.add(user)
    
    db.session.commit()
    
    print("✅ Done!")
    print(f"Username: {user.username}")
    print(f"Password: DeptPass123")
    print(f"Role: {user.role}")
    print(f"Active: {user.is_active}")