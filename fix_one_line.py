"""
SUPER SIMPLE FIX - Changes one line in app.py
This fixes "audit_logger is not defined" error
"""

import shutil
from datetime import datetime

def fix_one_line():
    """Change the audit_logger import line"""
    
    # Backup
    backup = f"app_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.py"
    shutil.copy('app.py', backup)
    print(f"✅ Backup: {backup}")
    
    # Read
    with open('app.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Old import
    old = 'from utils.audit_logger import log_audit_action_safe, log_audit_action_enhanced, log_security_event'
    
    # New import
    new = 'from utils import audit_logger'
    
    # Replace
    if old in content:
        content = content.replace(old, new)
        
        # Write
        with open('app.py', 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("✅ Fixed!")
        print()
        print("Changed:")
        print("  OLD: from utils.audit_logger import log_audit_action_safe, ...")
        print("  NEW: from utils import audit_logger")
        return True
    else:
        print("⚠️  Import line not found or already fixed")
        return False

if __name__ == '__main__':
    print("=" * 60)
    print("FIX 'audit_logger is not defined'")
    print("=" * 60)
    print()
    print("This changes ONE line in app.py")
    print()
    
    input("Press Enter to fix...")
    print()
    
    success = fix_one_line()
    
    if success:
        print()
        print("✅ DONE! The warnings should disappear now.")
    else:
        print()
        print("See ONE_LINE_FIX.md for manual instructions")
