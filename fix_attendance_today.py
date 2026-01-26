# Fix the attendance/today endpoint
with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Find and replace the buggy line
old_code = '''            # Get department name
            department = Department.query.get(employee.department_id)

            if attendance:
                result.append({
                    'id': attendance.id,
                    'employee_id': employee.id,
                    'employee_name': employee.name,
                    'department': department.name if department else 'N/A','''

new_code = '''            if attendance:
                result.append({
                    'id': attendance.id,
                    'employee_id': employee.id,
                    'employee_name': employee.name,
                    'department': employee.department,  # Department is stored as string'''

content = content.replace(old_code, new_code)

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(content)

print('✅ Fixed attendance/today endpoint!')
