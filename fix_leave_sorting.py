import re

with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Find the leave requests query for Admin/HR
old_query = 'leaves = LeaveRequest.query.all()'
new_query = 'leaves = LeaveRequest.query.order_by(LeaveRequest.id.desc()).all()'

content = content.replace(old_query, new_query)

# Also fix the employee query
old_emp_query = 'leaves = LeaveRequest.query.filter_by(employee_id=employee.id).all()'
new_emp_query = 'leaves = LeaveRequest.query.filter_by(employee_id=employee.id).order_by(LeaveRequest.id.desc()).all()'

content = content.replace(old_emp_query, new_emp_query)

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(content)

print('✅ Backend updated to sort by newest first!')
