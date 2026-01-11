# cleanup_audit_logs.py
from app import app, db
from models import AuditTrail
from datetime import datetime, timedelta

def cleanup_old_audit_logs(days=180):
    """Delete audit logs older than `days` days (default 6 months)."""
    with app.app_context():
        threshold = datetime.utcnow() - timedelta(days=days)
        old_logs = AuditTrail.query.filter(AuditTrail.timestamp < threshold).all()
        count = len(old_logs)
        for log in old_logs:
            db.session.delete(log)
        db.session.commit()
        print(f"✅ Deleted {count} old audit logs older than {days} days.")

if __name__ == "__main__":
    cleanup_old_audit_logs()
