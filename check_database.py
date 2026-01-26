from app import app, db, User, Employee, LeaveRequest, Payroll, Attendance

with app.app_context():
    print('=' * 50)
    print('DATABASE STATUS CHECK')
    print('=' * 50)
    
    users = User.query.count()
    employees = Employee.query.count()
    leave_requests = LeaveRequest.query.count()
    payrolls = Payroll.query.count()
    attendances = Attendance.query.count()
    
    print(f'✅ Users: {users}')
    print(f'✅ Employees: {employees}')
    print(f'✅ Leave Requests: {leave_requests}')
    print(f'✅ Payroll Records: {payrolls}')
    print(f'✅ Attendance Records: {attendances}')
    print('=' * 50)
    
    # Check for test users
    print('\nTEST USERS:')
    print('-' * 50)
    admin = User.query.filter_by(role='Admin').first()
    hr = User.query.filter_by(role='HR Officer').first()
    employee = User.query.filter_by(role='Employee').first()
    
    if admin:
        print(f'✅ Admin user: {admin.username}')
    else:
        print('❌ No Admin user found')
    
    if hr:
        print(f'✅ HR Officer user: {hr.username}')
    else:
        print('⚠️  No HR Officer found')
        
    if employee:
        print(f'✅ Employee user: {employee.username}')
    else:
        print('❌ No Employee user found')
    
    print('=' * 50)
    print('\nDatabase check complete!')
