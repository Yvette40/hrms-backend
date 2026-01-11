# ==============================================================================
# FILE: backend/utils/audit_logger.py (ENHANCED VERSION)
# NEW FEATURES: Old/New value tracking, Action severity, Security events
# ==============================================================================

from datetime import datetime
from flask import g, has_app_context
import json

def log_audit_action_enhanced(
    db, 
    action, 
    module, 
    details=None,
    action_type="Normal",  # Normal, Sensitive, Critical
    old_value=None,
    new_value=None,
    user_id=None, 
    ip_address=None
):
    """
    Enhanced audit logging with old/new value tracking and severity
    
    Args:
        db: Database session
        action: Action performed (e.g., "UPDATE_EMPLOYEE")
        module: Module name (e.g., "EMPLOYEE", "PAYROLL")
        details: Human-readable description
        action_type: Severity - Normal, Sensitive, Critical
        old_value: Dict of old values (will be JSON serialized)
        new_value: Dict of new values (will be JSON serialized)
        user_id: User ID (optional, will get from context)
        ip_address: IP address (optional)
    """
    from models import AuditTrail
    
    if user_id is None:
        user_id = getattr(g, "current_user_id", None) or "anonymous"
    
    # Serialize old/new values to JSON
    old_value_json = json.dumps(old_value) if old_value else None
    new_value_json = json.dumps(new_value) if new_value else None
    
    def _log():
        try:
            log_entry = AuditTrail(
                user_id=user_id,
                action=action,
                module=module,
                action_type=action_type,
                old_value=old_value_json,
                new_value=new_value_json,
                details=details,
                ip_address=ip_address,
                timestamp=datetime.utcnow()
            )
            db.session.add(log_entry)
            db.session.commit()
            
            # Visual indicator for critical actions
            indicator = "🔴" if action_type == "Critical" else "🟡" if action_type == "Sensitive" else "🟢"
            print(f"[AUDIT {indicator}] {action} ({module}) - {details} | user: {user_id}")
        except Exception as e:
            print(f"⚠️ Audit log failed: {e}")
    
    if not has_app_context():
        from app import app
        with app.app_context():
            _log()
    else:
        _log()


def log_security_event(db, event_type, username=None, ip_address=None, details=None, severity="Low"):
    """
    Log security-related events (separate from audit trail)
    
    Args:
        event_type: LOGIN_FAILED, UNAUTHORIZED_ACCESS, ROLE_VIOLATION, etc.
        username: Username attempting action
        ip_address: IP address
        details: Additional context
        severity: Low, Medium, High, Critical
    """
    from models import SecurityEvent
    
    def _log():
        try:
            event = SecurityEvent(
                event_type=event_type,
                username=username,
                ip_address=ip_address,
                details=details,
                severity=severity,
                timestamp=datetime.utcnow()
            )
            db.session.add(event)
            db.session.commit()
            
            print(f"[SECURITY 🚨] {event_type} | User: {username} | Severity: {severity}")
        except Exception as e:
            print(f"⚠️ Security log failed: {e}")
    
    if not has_app_context():
        from app import app
        with app.app_context():
            _log()
    else:
        _log()


def log_sod_check(db, rule_name, user_id, status, action_attempted=None, details=None):
    """
    Log separation of duties checks
    
    Args:
        rule_name: Name of SOD rule (e.g., "Cannot approve own payroll")
        user_id: User attempting action
        status: BLOCKED, ALLOWED, WARNING
        action_attempted: What they tried to do
        details: Additional context
    """
    from models import SeparationOfDutiesLog
    
    def _log():
        try:
            sod_log = SeparationOfDutiesLog(
                rule_name=rule_name,
                action_attempted=action_attempted,
                user_id=user_id,
                status=status,
                details=details,
                timestamp=datetime.utcnow()
            )
            db.session.add(sod_log)
            db.session.commit()
            
            symbol = "⛔" if status == "BLOCKED" else "✅" if status == "ALLOWED" else "⚠️"
            print(f"[SOD {symbol}] {rule_name} | User: {user_id} | Status: {status}")
        except Exception as e:
            print(f"⚠️ SOD log failed: {e}")
    
    if not has_app_context():
        from app import app
        with app.app_context():
            _log()
    else:
        _log()


# Backward compatibility - keep old function
def log_audit_action_safe(db, action_type, description, module=None, user_id=None, ip_address=None):
    """
    Legacy function for backward compatibility
    Redirects to enhanced logger
    """
    log_audit_action_enhanced(
        db=db,
        action=action_type,
        module=module or "GENERAL",
        details=description,
        action_type="Normal",
        user_id=user_id,
        ip_address=ip_address
    )
