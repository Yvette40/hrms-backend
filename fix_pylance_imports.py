"""
Fix Missing Model Imports in app.py
This adds UserSettings and Notification to the imports
"""

import re
import shutil
from datetime import datetime

def fix_imports():
    """Add missing model imports to app.py"""
    
    # Backup
    backup_name = f"app_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.py"
    print(f"📋 Creating backup: {backup_name}")
    shutil.copy('app.py', backup_name)
    
    # Read file
    with open('app.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find the models import line
    old_import = r'from models import.*LeaveRequest.*'
    
    if re.search(old_import, content):
        # Replace with new import including UserSettings and Notification
        new_import = """from models import (
    User, Employee, Attendance, Payroll, AuditTrail, Anomaly, 
    ApprovalRequest, SecurityEvent, SeparationOfDutiesLog, 
    LeaveRequest, Notification, UserSettings
)"""
        
        content = re.sub(
            r'from models import[^)]*LeaveRequest[^\n]*',
            new_import,
            content,
            count=1
        )
        
        # Write back
        with open('app.py', 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("✅ Added missing imports: Notification, UserSettings")
        print(f"📁 Backup saved as: {backup_name}")
        return True
    else:
        print("⚠️ Could not find models import line")
        print("   Please add manually")
        return False

if __name__ == '__main__':
    print("=" * 60)
    print("FIX MISSING MODEL IMPORTS")
    print("=" * 60)
    print()
    print("This will add Notification and UserSettings to imports")
    print("This fixes the Pylance warnings in VS Code")
    print()
    
    response = input("Continue? (y/n): ").strip().lower()
    
    if response == 'y':
        success = fix_imports()
        
        if success:
            print()
            print("=" * 60)
            print("✅ IMPORTS FIXED!")
            print("=" * 60)
            print()
            print("The Pylance warnings should disappear now.")
            print("Your app is already running - no need to restart!")
        else:
            print()
            print("Manual fix needed:")
            print("Find: from models import ... LeaveRequest")
            print("Add: , Notification, UserSettings")
    else:
        print("\n❌ Cancelled")
        print("Note: These are just IDE warnings, not errors.")
        print("Your app is running fine!")
