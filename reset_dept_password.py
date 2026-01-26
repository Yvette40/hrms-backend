from app import app, db, User

with app.app_context():
    dept_user = User.query.filter_by(username='dept_manager').first()
    
    if dept_user:
        # Reset password to 'dept123'
        dept_user.set_password('dept123')
        db.session.commit()
        
        print('✅ Password reset successful!')
        print('=' * 50)
        print('DEPARTMENT MANAGER LOGIN:')
        print('=' * 50)
        print('Username: dept_manager')
        print('Password: dept123')
        print('=' * 50)
    else:
        print('❌ User not found')
