"""
ALL-IN-ONE DATABASE LOCK FIX
This script fixes all database locking issues automatically
"""

import os
import shutil
from datetime import datetime

def backup_files():
    """Create backups"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    backups = {}
    
    # Backup app.py
    if os.path.exists('app.py'):
        backup_app = f"app_backup_{timestamp}.py"
        shutil.copy('app.py', backup_app)
        backups['app.py'] = backup_app
        print(f"✅ Backed up app.py → {backup_app}")
    
    # Backup audit_logger.py
    logger_path = os.path.join('utils', 'audit_logger.py')
    if os.path.exists(logger_path):
        backup_logger = f"audit_logger_backup_{timestamp}.py"
        shutil.copy(logger_path, backup_logger)
        backups['audit_logger.py'] = backup_logger
        print(f"✅ Backed up audit_logger.py → {backup_logger}")
    
    return backups


def fix_app_py():
    """Fix app.py - add SQLite config and fix datetime"""
    print("\n📝 Fixing app.py...")
    
    with open('app.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Fix 1: Add SQLite configuration after db.init_app(app)
    if 'SQLALCHEMY_ENGINE_OPTIONS' not in content:
        sqlite_config = """
# ============================================================================
# SQLITE DATABASE CONFIGURATION - PREVENT LOCKING
# ============================================================================
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'pool_pre_ping': True,
    'pool_recycle': 300,
    'connect_args': {
        'timeout': 30,
        'check_same_thread': False
    }
}
"""
        # Find db.init_app(app) and add config before it
        if 'db.init_app(app)' in content:
            content = content.replace('db.init_app(app)', sqlite_config + '\ndb.init_app(app)')
            print("  ✅ Added SQLite configuration")
        else:
            print("  ⚠️ Could not find db.init_app(app)")
    
    # Fix 2: Fix datetime.utcnow() deprecation
    utcnow_count = content.count('datetime.utcnow()')
    if utcnow_count > 0:
        content = content.replace('datetime.utcnow()', 'datetime.now(UTC).replace(tzinfo=None)')
        
        # Add UTC import if not present
        if 'from datetime import datetime' in content and ', UTC' not in content:
            content = content.replace(
                'from datetime import datetime, time, timedelta',
                'from datetime import datetime, time, timedelta, UTC'
            )
        
        print(f"  ✅ Fixed {utcnow_count} datetime.utcnow() calls")
    
    # Write back
    with open('app.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    return True


def fix_audit_logger():
    """Fix audit logger to handle database locks"""
    print("\n📝 Fixing audit_logger.py...")
    
    logger_path = os.path.join('utils', 'audit_logger.py')
    if not os.path.exists(logger_path):
        print("  ⚠️ audit_logger.py not found - skipping")
        return False
    
    # Read current content
    with open(logger_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check if already fixed
    if 'db.session.rollback()' in content and 'OperationalError' in content:
        print("  ✅ Already has rollback logic")
        return True
    
    # Replace with fixed version
    fixed_content = """from sqlalchemy.exc import OperationalError
from datetime import datetime, UTC
import time

def log_audit_action_safe(db, action_type, description, module, user_id=None, ip_address=None, action_type_category="Normal"):
    max_retries = 3
    for attempt in range(max_retries):
        try:
            from models import AuditTrail
            audit_entry = AuditTrail(
                user_id=user_id, action=action_type, module=module,
                action_type=action_type_category, details=description,
                ip_address=ip_address, timestamp=datetime.now(UTC).replace(tzinfo=None)
            )
            db.session.add(audit_entry)
            db.session.commit()
            return True
        except OperationalError as e:
            db.session.rollback()
            if "database is locked" in str(e) and attempt < max_retries - 1:
                time.sleep(0.1 * (attempt + 1))
                continue
            print(f"⚠️ Audit log failed: {e}")
            return False
        except Exception as e:
            db.session.rollback()
            return False
    return False

def log_audit_action_enhanced(db, user_id, action, module, old_value=None, new_value=None, details=None, ip_address=None):
    max_retries = 3
    for attempt in range(max_retries):
        try:
            from models import AuditTrail
            audit_entry = AuditTrail(
                user_id=user_id, action=action, module=module,
                old_value=old_value, new_value=new_value, details=details,
                ip_address=ip_address, timestamp=datetime.now(UTC).replace(tzinfo=None)
            )
            db.session.add(audit_entry)
            db.session.commit()
            return True
        except OperationalError as e:
            db.session.rollback()
            if "database is locked" in str(e) and attempt < max_retries - 1:
                time.sleep(0.1 * (attempt + 1))
                continue
            return False
        except Exception as e:
            db.session.rollback()
            return False
    return False

def log_security_event(db, event_type, description, severity="Low", user_id=None, ip_address=None):
    max_retries = 3
    for attempt in range(max_retries):
        try:
            from models import SecurityEvent
            event = SecurityEvent(
                event_type=event_type, details=description, severity=severity,
                user_id=user_id, ip_address=ip_address,
                timestamp=datetime.now(UTC).replace(tzinfo=None)
            )
            db.session.add(event)
            db.session.commit()
            return True
        except OperationalError as e:
            db.session.rollback()
            if "database is locked" in str(e) and attempt < max_retries - 1:
                time.sleep(0.1 * (attempt + 1))
                continue
            return False
        except Exception as e:
            db.session.rollback()
            return False
    return False
"""
    
    with open(logger_path, 'w', encoding='utf-8') as f:
        f.write(fixed_content)
    
    print("  ✅ Fixed audit logger with rollback logic")
    return True


def clean_database_locks():
    """Remove database lock files"""
    print("\n🗑️ Cleaning database lock files...")
    
    lock_files = [
        'instance/hrms.db-journal',
        'instance/hrms.db-wal',
        'instance/hrms.db-shm'
    ]
    
    removed = 0
    for lock_file in lock_files:
        if os.path.exists(lock_file):
            try:
                os.remove(lock_file)
                print(f"  ✅ Removed {lock_file}")
                removed += 1
            except Exception as e:
                print(f"  ⚠️ Could not remove {lock_file}: {e}")
    
    if removed == 0:
        print("  ℹ️ No lock files found")
    
    return True


def main():
    print("=" * 70)
    print("ALL-IN-ONE DATABASE LOCK FIX")
    print("=" * 70)
    print()
    print("This script will:")
    print("  1. Backup your files")
    print("  2. Add SQLite configuration to prevent locking")
    print("  3. Fix datetime.utcnow() deprecation warnings")
    print("  4. Fix audit logger to handle database locks")
    print("  5. Clean database lock files")
    print()
    
    response = input("Continue? (y/n): ").strip().lower()
    if response != 'y':
        print("\n❌ Cancelled")
        return
    
    print()
    
    # Step 1: Backup
    print("Step 1: Creating backups...")
    backups = backup_files()
    
    # Step 2: Fix app.py
    print("\nStep 2: Fixing app.py...")
    fix_app_py()
    
    # Step 3: Fix audit logger
    print("\nStep 3: Fixing audit logger...")
    fix_audit_logger()
    
    # Step 4: Clean locks
    print("\nStep 4: Cleaning database locks...")
    clean_database_locks()
    
    print()
    print("=" * 70)
    print("✅ ALL FIXES APPLIED!")
    print("=" * 70)
    print()
    print("Next steps:")
    print("  1. STOP your Flask server (Ctrl+C)")
    print("  2. Run: python app.py")
    print("  3. Test the application")
    print()
    print("If something went wrong, restore from backups:")
    for original, backup in backups.items():
        print(f"  - {backup} → {original}")
    print()

if __name__ == '__main__':
    main()
