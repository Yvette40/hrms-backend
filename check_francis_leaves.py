from app import app, db, LeaveRequest, Employee

with app.app_context():
    # Find Francis
    francis = Employee.query.filter_by(name='Francis Njoroge').first()
    
    if francis:
        print(f'Francis ID: {francis.id}')
        
        # Get his leave requests
        leaves = LeaveRequest.query.filter_by(employee_id=francis.id).all()
        
        print(f'\nFrancis has {len(leaves)} leave requests:')
        for leave in leaves:
            print(f'  - {leave.leave_type}: {leave.start_date} to {leave.end_date} ({leave.status})')
    else:
        print('Francis not found')
    
    # Check all leave requests
    all_leaves = LeaveRequest.query.all()
    print(f'\nTotal leave requests in database: {len(all_leaves)}')
