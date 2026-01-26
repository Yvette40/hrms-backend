from app import app, db, User, Employee

with app.app_context():
    # Check fnjoroge user
    user = User.query.filter_by(username='fnjoroge').first()
    
    if user:
        print(f'User: {user.username}')
        print(f'User ID: {user.id}')
        print(f'Role: {user.role}')
        
        # Check if linked to employee
        if user.employee_profile:
            emp = user.employee_profile[0]
            print(f'\n✅ Linked to Employee:')
            print(f'   Name: {emp.name}')
            print(f'   ID: {emp.id}')
            print(f'   Active: {emp.active}')
        else:
            print('\n❌ NOT linked to any employee!')
            
            # Check if there's an employee with matching user_id
            emp = Employee.query.filter_by(user_id=user.id).first()
            if emp:
                print(f'Found employee with user_id={user.id}: {emp.name}')
    else:
        print('User not found')
