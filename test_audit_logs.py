from app import app, db
from models import User, Employee, AuditTrail
from utils.audit_logger import log_audit_action_safe
from datetime import datetime

# ✅ Run everything inside app context
with app.app_context():
    # Make sure admin exists
    admin = User.query.filter_by(username="admin").first()
    if not admin:
        admin = User(username="admin", role="Admin")
        admin.set_password("AdminPass123")
        db.session.add(admin)
        db.session.commit()
        print("✅ Default admin created")

    # ------------------------
    # Test log_audit_action_safe directly
    # ------------------------
    print("Logging test action directly...")
    log_audit_action_safe(db, "TEST_DIRECT", "Testing log_audit_action_safe", module="DEV_TEST")

    # ------------------------
    # Test creating an employee
    # ------------------------
    emp = Employee(name="Direct Test Employee", national_id="D12345", base_salary=1000)
    db.session.add(emp)
    db.session.commit()

    # Log the action with correct user
    log_audit_action_safe(db, "Created Employee", f"Added employee {emp.name}", module="Employee")

    # ------------------------
    # Fetch and print audit logs
    # ------------------------
    logs = AuditTrail.query.order_by(AuditTrail.timestamp.desc()).all()
    print("\n===== AUDIT LOGS =====")
    for log in logs:
        user = User.query.get(log.user_id)
        print(f"{log.timestamp} | {user.username if user else 'Unknown'} | {log.action} | {log.module} | {log.details}")
    print("======================")
