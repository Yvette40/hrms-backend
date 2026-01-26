from app import app, db, User, Employee

with app.app_context():
    # Find mjoroge user
    user = User.query.filter_by(username='mjoroge').first()
    
    if user:
        print(f'User found: {user.username}')
        print(f'Role: {user.role}')
        print(f'User ID: {user.id}')
        
        # Check if already linked
        if user.employee_profile:
            print(f'Already linked to employee: {user.employee_profile[0].name}')
        else:
            # Find an employee without a user account to link
            unlinked_employee = Employee.query.filter_by(user_id=None).first()
            
            if unlinked_employee:
                # Link them
                unlinked_employee.user_id = user.id
                db.session.commit()
                print(f'\n✅ Linked user {user.username} to employee:')
                print(f'   Name: {unlinked_employee.name}')
                print(f'   ID: {unlinked_employee.id}')
                print(f'   Department: {unlinked_employee.department}')
            else:
                print('No unlinked employees found')
    else:
        print('❌ User mjoroge not found')
