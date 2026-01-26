from app import app, db, Employee, LeaveRequest
from datetime import datetime

with app.app_context():
    # Check if leave balance tracking exists
    emp = Employee.query.first()
    
    if emp:
        print(f'Employee: {emp.name}')
        
        # Check for leave balance fields
        if hasattr(emp, 'annual_leave_balance'):
            print(f'  Annual Leave Balance: {emp.annual_leave_balance}')
        else:
            print('  ❌ No leave balance field found')
        
        # Calculate used leave
        year = datetime.now().year
        leaves = LeaveRequest.query.filter_by(
            employee_id=emp.id,
            status='Approved'
        ).all()
        
        total_days = sum(l.days_requested for l in leaves)
        print(f'  Total approved leave days: {total_days}')
