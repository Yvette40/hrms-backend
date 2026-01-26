# Fix for health check endpoint
import re

# Read the file
with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Find and replace the health check query
# Look for: db.session.execute('SELECT 1')
# Replace with: db.session.execute(text('SELECT 1'))

old_pattern = r"db\.session\.execute\('SELECT 1'\)"
new_code = "db.session.execute(text('SELECT 1'))"

content = re.sub(old_pattern, new_code, content)

# Also need to make sure text is imported
if 'from sqlalchemy import' in content:
    # Check if text is already imported
    if ', text' not in content and 'text,' not in content and 'text)' not in content:
        # Add text to the imports
        content = content.replace('from sqlalchemy import', 'from sqlalchemy import text,', 1)

# Write back
with open('app.py', 'w', encoding='utf-8') as f:
    f.write(content)

print('✅ Health check endpoint fixed!')
