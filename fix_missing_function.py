"""
Quick Fix for Missing log_sod_check Function
This adds the missing function to audit_logger.py
"""

import os
import shutil
from datetime import datetime

def fix_audit_logger():
    """Add missing log_sod_check function to audit_logger.py"""
    
    logger_path = os.path.join('utils', 'audit_logger.py')
    
    if not os.path.exists(logger_path):
        print("❌ utils/audit_logger.py not found!")
        return False
    
    # Backup
    backup_name = f"audit_logger_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.py"
    shutil.copy(logger_path, backup_name)
    print(f"✅ Backup created: {backup_name}")
    
    # Complete audit logger with ALL functions
    complete_content = '''"""
Complete Audit Logger with Database Lock Protection
Includes all required functions for HRMS system
"""

from sqlalchemy.exc import OperationalError
from datetime import datetime, UTC
import time


def log_audit_action_safe(db, action_type, description, module, user_id=None, ip_address=None, action_type_category="Normal"):
    """Safe audit logging with automatic rollback on failure"""
    max_retries = 3
    
    for attempt in range(max_retries):
        try:
            from models import AuditTrail
            
            audit_entry = AuditTrail(
                user_id=user_id,
                action=action_type,
                module=module,
                action_type=action_type_category,
                details=description,
                ip_address=ip_address,
                timestamp=datetime.now(UTC).replace(tzinfo=None)
            )
            
            db.session.add(audit_entry)
            db.session.flush()
            db.session.commit()
            return True
            
        except OperationalError as e:
            db.session.rollback()
            if "database is locked" in str(e) and attempt < max_retries - 1:
                time.sleep(0.1 * (attempt + 1))
                continue
            else:
                print(f"⚠️ Audit log failed: {e}")
                return False
                
        except Exception as e:
            db.session.rollback()
            print(f"⚠️ Audit log error: {e}")
            return False
    
    return False


def log_audit_action_enhanced(db, user_id, action, module, old_value=None, new_value=None, details=None, ip_address=None):
    """Enhanced audit logging with retry logic"""
    max_retries = 3
    
    for attempt in range(max_retries):
        try:
            from models import AuditTrail
            
            audit_entry = AuditTrail(
                user_id=user_id,
                action=action,
                module=module,
                old_value=old_value,
                new_value=new_value,
                details=details,
                ip_address=ip_address,
                timestamp=datetime.now(UTC).replace(tzinfo=None)
            )
            
            db.session.add(audit_entry)
            db.session.flush()
            db.session.commit()
            return True
            
        except OperationalError as e:
            db.session.rollback()
            if "database is locked" in str(e) and attempt < max_retries - 1:
                time.sleep(0.1 * (attempt + 1))
                continue
            else:
                return False
                
        except Exception as e:
            db.session.rollback()
            return False
    
    return False


def log_security_event(db, event_type, description, severity="Low", user_id=None, ip_address=None):
    """Log security events with retry logic"""
    max_retries = 3
    
    for attempt in range(max_retries):
        try:
            from models import SecurityEvent
            
            event = SecurityEvent(
                event_type=event_type,
                details=description,
                severity=severity,
                user_id=user_id,
                ip_address=ip_address,
                timestamp=datetime.now(UTC).replace(tzinfo=None)
            )
            
            db.session.add(event)
            db.session.flush()
            db.session.commit()
            return True
            
        except OperationalError as e:
            db.session.rollback()
            if "database is locked" in str(e) and attempt < max_retries - 1:
                time.sleep(0.1 * (attempt + 1))
                continue
            else:
                return False
                
        except Exception as e:
            db.session.rollback()
            return False
    
    return False


def log_sod_check(db, check_type, user_id, action, result, details=None):
    """
    Log Separation of Duties (SOD) checks
    Required by sod_checker.py
    """
    max_retries = 3
    
    for attempt in range(max_retries):
        try:
            from models import SeparationOfDutiesLog
            
            sod_log = SeparationOfDutiesLog(
                check_type=check_type,
                user_id=user_id,
                action=action,
                result=result,
                details=details,
                timestamp=datetime.now(UTC).replace(tzinfo=None)
            )
            
            db.session.add(sod_log)
            db.session.flush()
            db.session.commit()
            return True
            
        except OperationalError as e:
            db.session.rollback()
            if "database is locked" in str(e) and attempt < max_retries - 1:
                time.sleep(0.1 * (attempt + 1))
                continue
            else:
                print(f"⚠️ SOD log failed: {e}")
                return False
                
        except Exception as e:
            db.session.rollback()
            print(f"⚠️ SOD log error: {e}")
            return False
    
    return False


# Backward compatibility aliases
def log_action(db, user_id, action, module, details=None, ip_address=None):
    """Alias for log_audit_action_safe"""
    return log_audit_action_safe(
        db=db,
        action_type=action,
        description=details or action,
        module=module,
        user_id=user_id,
        ip_address=ip_address
    )
'''
    
    # Write the complete content
    with open(logger_path, 'w', encoding='utf-8') as f:
        f.write(complete_content)
    
    print("✅ Added log_sod_check function to audit_logger.py")
    print("✅ All functions now available")
    
    return True


if __name__ == '__main__':
    print("=" * 60)
    print("FIX MISSING log_sod_check FUNCTION")
    print("=" * 60)
    print()
    
    if not os.path.exists('utils'):
        print("❌ 'utils' directory not found!")
        print("   Run this script from your project root directory")
        exit(1)
    
    print("This will add the missing log_sod_check function")
    print("to utils/audit_logger.py")
    print()
    
    response = input("Continue? (y/n): ").strip().lower()
    
    if response == 'y':
        success = fix_audit_logger()
        
        if success:
            print()
            print("=" * 60)
            print("✅ FIX COMPLETE!")
            print("=" * 60)
            print()
            print("Now run: python app.py")
        else:
            print()
            print("❌ Fix failed")
    else:
        print("\n❌ Cancelled")
