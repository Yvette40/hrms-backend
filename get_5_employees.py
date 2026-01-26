from app import app, db, User, Employee

with app.app_context():
    print('=' * 60)
    print('5 EMPLOYEE ACCOUNTS FOR TESTING')
    print('=' * 60)
    
    # Get 5 employees with user accounts
    employees_with_users = User.query.filter_by(role='Employee').limit(5).all()
    
    print('\nUsername | Password | Employee Name | Department')
    print('-' * 60)
    
    for user in employees_with_users:
        # Get linked employee
        employee = Employee.query.filter_by(user_id=user.id).first()
        
        if employee:
            print(f'{user.username:15} | employee123 | {employee.name:20} | {employee.department}')
        else:
            print(f'{user.username:15} | employee123 | (No employee linked)')
    
    print('\n' + '=' * 60)
    print('All passwords are: employee123')
    print('=' * 60)
