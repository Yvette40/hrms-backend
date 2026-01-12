# ==========================================
# FIX FOR APP.PY - DATABASE INITIALIZATION
# ==========================================
# This script fixes the "unable to open database file" error

import os

print("🔧 Fixing app.py database initialization issue...")

# Path to app.py
app_py_path = r"K:\YVETTE\BIT 4.2\2a project\HRMS_Project\app.py"

# Read the file
with open(app_py_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Find and comment out the problematic section
new_lines = []
in_problematic_section = False
section_start = None

for i, line in enumerate(lines, 1):
    # Look for the problematic section
    if 'with app.app_context():' in line and i < 300:  # Around line 288
        in_problematic_section = True
        section_start = i
        new_lines.append('# ' + line)  # Comment it out
        print(f"  Line {i}: Commenting out 'with app.app_context():'")
    elif in_problematic_section and (line.strip().startswith('db.create_all()') or 
                                      line.strip().startswith('print("✅ Database') or
                                      line.strip().startswith('init_database()')):
        new_lines.append('# ' + line)  # Comment it out
        print(f"  Line {i}: Commenting out '{line.strip()[:50]}'")
        if 'init_database()' in line:
            in_problematic_section = False  # End of section
    else:
        new_lines.append(line)

# Write back
with open(app_py_path, 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

print("\n✅ Fixed! The problematic database initialization has been commented out.")
print("\n📝 What was changed:")
print("   - Commented out the 'with app.app_context():' block at line ~288")
print("   - Commented out db.create_all() and init_database()")
print("\n🎯 Now you need to:")
print("   1. Open Python and create the database manually:")
print("      python")
print("      >>> from app import app, db")
print("      >>> with app.app_context():")
print("      >>>     db.create_all()")
print("      >>>     print('Done!')")
print("      >>> exit()")
print("\n   2. Then run: python app.py")
