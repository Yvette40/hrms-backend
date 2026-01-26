from app import app, db, User, Employee

with app.app_context():
    print('=' * 60)
    print('SEARCHING FOR FRANCIS NJOROGE')
    print('=' * 60)
    
    # 1. Search for user 'mjoroge'
    print('\n1️⃣ CHECKING USER "mjoroge":')
    print('-' * 60)
    user = User.query.filter_by(username='mjoroge').first()
    if user:
        print(f'✅ User found!')
        print(f'   Username: {user.username}')
        print(f'   ID: {user.id}')
        print(f'   Role: {user.role}')
        print(f'   Email: {user.email}')
        print(f'   User ID linked to employee: {user.employee_profile[0].id if user.employee_profile else "NO"}')
    else:
        print('❌ User "mjoroge" NOT found')
    
    # 2. Search for employee 'Francis Njoroge'
    print('\n2️⃣ CHECKING EMPLOYEE "Francis Njoroge":')
    print('-' * 60)
    
    # Try exact match
    employee = Employee.query.filter_by(name='Francis Njoroge').first()
    if employee:
        print(f'✅ Employee found!')
        print(f'   Name: {employee.name}')
        print(f'   ID: {employee.id}')
        print(f'   Email: {employee.email}')
        print(f'   Department: {employee.department}')
        print(f'   Position: {employee.position}')
        print(f'   User ID: {employee.user_id} {"(LINKED)" if employee.user_id else "(NOT LINKED)"}')
        
        if employee.user_id:
            linked_user = User.query.get(employee.user_id)
            if linked_user:
                print(f'   Linked to user: {linked_user.username}')
    else:
        # Try partial match
        employees = Employee.query.filter(
            Employee.name.ilike('%francis%njoroge%')
        ).all()
        
        if employees:
            print(f'✅ Found {len(employees)} similar employee(s):')
            for emp in employees:
                print(f'\n   Name: {emp.name}')
                print(f'   ID: {emp.id}')
                print(f'   User ID: {emp.user_id or "NOT LINKED"}')
        else:
            print('❌ No employee found with name containing "francis njoroge"')
    
    # 3. Show linking options
    print('\n3️⃣ LINKING STATUS:')
    print('-' * 60)
    
    if user and employee:
        if employee.user_id == user.id:
            print('✅ User and Employee are already linked!')
        elif employee.user_id:
            other_user = User.query.get(employee.user_id)
            print(f'⚠️  Employee is linked to different user: {other_user.username if other_user else "Unknown"}')
        elif user.employee_profile:
            other_emp = user.employee_profile[0]
            print(f'⚠️  User is linked to different employee: {other_emp.name}')
        else:
            print('⚠️  User and Employee exist but NOT linked')
            print('   Ready to link them!')
    
    print('\n' + '=' * 60)
