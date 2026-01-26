from app import app, db, User

with app.app_context():
    dept_manager = User.query.filter_by(role='Department Manager').first()
    
    if dept_manager:
        print(f'✅ Department Manager user: {dept_manager.username}')
        print(f'   Email: {dept_manager.email}')
        print(f'   Role: {dept_manager.role}')
    else:
        print('❌ No Department Manager user found in database')
        print('\nWould you like me to create one?')
