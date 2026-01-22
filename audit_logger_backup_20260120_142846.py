from sqlalchemy.exc import OperationalError
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
