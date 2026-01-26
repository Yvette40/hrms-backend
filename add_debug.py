# Find line number of the check-in function
import re

with open('app.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Find the line with the role check
for i, line in enumerate(lines):
    if "if user.role != 'Employee':" in line and 'biometric' in ''.join(lines[max(0,i-20):i]):
        # Add debug print before the check
        indent = len(line) - len(line.lstrip())
        debug_line = ' ' * indent + 'print(f"DEBUG: User={user.username}, Role={user.role}, Expected=Employee")\n'
        lines.insert(i, debug_line)
        break

with open('app.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)

print('✅ Added debug logging')
