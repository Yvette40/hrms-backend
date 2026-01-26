# Replace your utils/audit_logger.py with this improved version:

from sqlalchemy.exc import OperationalError, SQLAlchemyError
from datetime import datetime, UTC
import time

def log_audit_action_safe(db, action_type, description, module, user_id=None, ip_address=None):
    """Safe audit logging with automatic rollback on failure"""
    max_retries = 3
    for attempt in range(max_retries):
        try:
            from models import AuditTrail
            audit_entry = AuditTrail(
                user_id=user_id,
                action=description,  # Human-readable description
                module=module,
                action_type=action_type,  # ✅ FIXED: Use action_type directly, not "Normal"
                details=description,
                ip_address=ip_address,
                timestamp=datetime.now(UTC).replace(tzinfo=None)
            )
            db.session.add(audit_entry)
            db.session.flush()
            db.session.commit()
            return True
        except OperationalError as e:
            if "database is locked" in str(e):
                if attempt < max_retries - 1:
                    time.sleep(0.1 * (attempt + 1))
                    db.session.rollback()
                    continue
            db.session.rollback()
            return False
        except Exception as e:
            db.session.rollback()
            print(f"Audit log error: {e}")
            return False
    return False


def log_audit_action_enhanced(db, user_id, action, module, old_value=None, new_value=None, details=None, ip_address=None):
    """Enhanced audit logging with retry"""
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
            if "database is locked" in str(e):
                db.session.rollback()
                if attempt < max_retries - 1:
                    time.sleep(0.1 * (attempt + 1))
                    continue
                else:
                    print(f"⚠️ Enhanced audit log failed (DB locked)")
                    return False
            else:
                db.session.rollback()
                return False
                
        except Exception as e:
            db.session.rollback()
            return False
    
    return False


def log_security_event(db, event_type, description, severity="Low", user_id=None, ip_address=None):
    """Log security events with retry"""
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
            if "database is locked" in str(e):
                db.session.rollback()
                if attempt < max_retries - 1:
                    time.sleep(0.1 * (attempt + 1))
                    continue
                else:
                    print(f"⚠️ Security event log failed (DB locked)")
                    return False
            else:
                db.session.rollback()
                return False
                
        except Exception as e:
            db.session.rollback()
            return False
    
    return False