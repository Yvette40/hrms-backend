from app import app, db, User, Employee
from datetime import datetime

with app.app_context():
    # Check if dept_manager user already exists
    existing = User.query.filter_by(username='dept_manager').first()
    
    if existing:
        print('⚠️  dept_manager user already exists!')
    else:
        # Create Department Manager user
        dept_user = User(
            username='dept_manager',
            role='Department Manager',
            email='deptmanager@hrms.com',
            phone='0712345678',
            is_active=True,
            last_login=None
        )
        dept_user.set_password('dept123')  # Password: dept123
        
        db.session.add(dept_user)
        db.session.commit()
        
        print('✅ Department Manager user created!')
        print('   Username: dept_manager')
        print('   Password: dept123')
        print('   Role: Department Manager')
