# Update app.py to use SHA instead of NHIF
with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Rename function
content = content.replace('def calculate_nhif(', 'def calculate_sha(')
content = content.replace('calculate_nhif(', 'calculate_sha(')

# Update variable names
content = content.replace('nhif = calculate_sha', 'sha = calculate_sha')
content = content.replace('\'nhif\':', '\'sha\':')
content = content.replace('nhif=calc[\'sha\']', 'sha=calc[\'sha\']')
content = content.replace('payslip.nhif', 'payslip.sha')
content = content.replace('[\'NHIF\',', '[\'SHA\',')

# Update comments
content = content.replace('NHIF deduction', 'SHA deduction')
content = content.replace('NHIF', 'SHA')

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(content)

print('✅ Backend updated to use SHA!')
