from app import app, db, User, Employee

with app.app_context():
    print('=' * 60)
    print('SEARCHING FOR MJOROGE IN DATABASE')
    print('=' * 60)
    
    # Check Users table - try different variations
    print('\n1️⃣ CHECKING USERS TABLE:')
    print('-' * 60)
    
    # Try exact match
    user = User.query.filter_by(username='mjoroge').first()
    if user:
        print(f'✅ Found user: {user.username}')
        print(f'   ID: {user.id}')
        print(f'   Role: {user.role}')
        print(f'   Email: {user.email}')
        print(f'   Active: {user.is_active}')
    else:
        print('❌ No user with username "mjoroge"')
    
    # Try case-insensitive search
    all_users = User.query.all()
    similar = [u for u in all_users if 'mjoroge' in u.username.lower()]
    if similar:
        print(f'\n📝 Found similar usernames:')
        for u in similar:
            print(f'   - {u.username} (ID: {u.id}, Role: {u.role})')
    
    # Check if there's a user with that email
    user_by_email = User.query.filter_by(email='mjoroge@hrms.com').first()
    if user_by_email:
        print(f'\n✅ Found user by email:')
        print(f'   Username: {user_by_email.username}')
        print(f'   ID: {user_by_email.id}')
    
    print('\n2️⃣ CHECKING EMPLOYEES TABLE:')
    print('-' * 60)
    
    # Check Employees table
    employees = Employee.query.filter(
        Employee.name.ilike('%mjoroge%')
    ).all()
    
    if employees:
        print(f'✅ Found {len(employees)} employee(s) with "mjoroge" in name:')
        for emp in employees:
            print(f'\n   Employee ID: {emp.id}')
            print(f'   Name: {emp.name}')
            print(f'   National ID: {emp.national_id}')
            print(f'   Email: {emp.email}')
            print(f'   Department: {emp.department}')
            print(f'   Position: {emp.position}')
            print(f'   User ID: {emp.user_id} {"(LINKED)" if emp.user_id else "(NOT LINKED)"}')
    else:
        print('❌ No employees with "mjoroge" in name')
    
    print('\n3️⃣ STATISTICS:')
    print('-' * 60)
    print(f'Total Users: {User.query.count()}')
    print(f'Total Employees: {Employee.query.count()}')
    print(f'Unlinked Employees: {Employee.query.filter_by(user_id=None).count()}')
    
    print('\n' + '=' * 60)
