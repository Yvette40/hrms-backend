from datetime import datetime, timedelta
from app import app, db
from models import AuditTrail

def cleanup_old_logs(days=90):
    """Delete audit logs older than `days`."""
    cutoff = datetime.utcnow() - timedelta(days=days)
    with app.app_context():
        deleted = AuditTrail.query.filter(AuditTrail.timestamp < cutoff).delete()
        db.session.commit()
        print(f"✅ Deleted {deleted} old audit logs.")
