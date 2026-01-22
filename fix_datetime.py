"""
Fix datetime.utcnow() deprecation warnings
This script replaces all datetime.utcnow() with datetime.now(UTC)
"""

import re
import shutil
from datetime import datetime

def fix_datetime_deprecation():
    """Replace all datetime.utcnow() with datetime.now(UTC)"""
    
    # Backup
    backup_name = f"app_backup_datetime_{datetime.now().strftime('%Y%m%d_%H%M%S')}.py"
    print(f"📋 Creating backup: {backup_name}")
    shutil.copy('app.py', backup_name)
    
    # Read file
    with open('app.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Count occurrences
    count = content.count('datetime.utcnow()')
    print(f"🔍 Found {count} occurrences of datetime.utcnow()")
    
    if count == 0:
        print("✅ No datetime.utcnow() found - already fixed!")
        return
    
    # Replace datetime.utcnow() with datetime.now(UTC).replace(tzinfo=None)
    new_content = content.replace(
        'datetime.utcnow()',
        'datetime.now(UTC).replace(tzinfo=None)'
    )
    
    # Make sure UTC is imported from datetime
    if 'from datetime import' in new_content and 'UTC' not in new_content:
        # Find the datetime import line
        new_content = new_content.replace(
            'from datetime import datetime, time, timedelta',
            'from datetime import datetime, time, timedelta, UTC'
        )
    
    # Write fixed file
    with open('app.py', 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print(f"✅ Fixed {count} occurrences")
    print(f"📁 Backup saved as: {backup_name}")

if __name__ == '__main__':
    print("=" * 60)
    print("Fix datetime.utcnow() Deprecation Warnings")
    print("=" * 60)
    print()
    
    response = input("Fix all datetime.utcnow() deprecation warnings? (y/n): ").lower()
    if response == 'y':
        fix_datetime_deprecation()
        print()
        print("✅ Done! Restart your Flask app: python app.py")
    else:
        print("❌ Cancelled")
