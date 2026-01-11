from app import app, db
from models import User, Employee, Payroll, Attendance, Anomaly, AuditTrail
from utils.audit_logger import log_audit_action_safe
from datetime import datetime, timedelta
import random

with app.app_context():
    # -------------------------------
    # 0️⃣ Clear previous test data
    # -------------------------------
    print("🧹 Clearing previous test data...")
    for model in [AuditTrail, Anomaly, Payroll, Attendance, Employee]:
        db.session.query(model).delete()
    db.session.commit()
    print("✅ Previous test data cleared")

    # -------------------------------
    # 1️⃣ Ensure admin exists
    # -------------------------------
    admin = User.query.filter_by(username="admin").first()
    if not admin:
        admin = User(username="admin", role="Admin")
        admin.set_password("AdminPass123")
        db.session.add(admin)
        db.session.commit()
        print("✅ Default admin created")

    # -------------------------------
    # 2️⃣ Direct audit log test
    # -------------------------------
    log_audit_action_safe(db, "TEST_DIRECT", "Direct audit log test", module="DEV_TEST")

    # -------------------------------
    # 3️⃣ Create multiple employees
    # -------------------------------
    employee_names = ["Alice", "Bob", "Charlie", "Diana"]
    employees = []
    for name in employee_names:
        emp = Employee(name=f"{name} Test", national_id=f"{name[:2].upper()}123", base_salary=1000)
        db.session.add(emp)
        employees.append(emp)
        log_audit_action_safe(db, "Created Employee", f"Added employee {emp.name}", module="Employee")
    db.session.commit()
    print("✅ Multiple test employees added")

    # -------------------------------
    # 4️⃣ Simulate 3 payroll cycles with attendance
    # -------------------------------
    for cycle in range(3):
        period_start = datetime.utcnow().date() - timedelta(days=30*(cycle+1))
        period_end = period_start + timedelta(days=29)
        print(f"\n💰 Running payroll cycle {cycle+1}: {period_start} to {period_end}")

        for emp in employees:
            # Random attendance: some present, some absent to trigger anomalies
            attendance_days = random.randint(0, 20)
            for day_offset in range(attendance_days):
                att_date = period_start + timedelta(days=day_offset)
                att = Attendance(employee_id=emp.id, date=att_date, status="Present")
                db.session.add(att)

            db.session.commit()

            anomaly_flag = attendance_days == 0
            payroll = Payroll(
                employee_id=emp.id,
                period_start=period_start,
                period_end=period_end,
                gross_salary=emp.base_salary,
                anomaly_flag=anomaly_flag
            )
            db.session.add(payroll)
            db.session.commit()
            log_audit_action_safe(db, "Ran Payroll", f"Processed payroll for {emp.name}", module="Payroll")

            # Detect anomaly
            if anomaly_flag:
                existing = Anomaly.query.filter_by(payroll_id=payroll.id).first()
                if not existing:
                    anomaly = Anomaly(
                        employee_id=emp.id,
                        payroll_id=payroll.id,
                        description=f"No attendance recorded for {emp.name} in payroll period",
                        severity="High"
                    )
                    db.session.add(anomaly)
                    db.session.commit()
                    log_audit_action_safe(db, "Detected Anomalies", f"Detected anomaly for {emp.name}", module="Anomaly")

    # -------------------------------
    # 5️⃣ Print all audit logs
    # -------------------------------
    logs = AuditTrail.query.order_by(AuditTrail.timestamp.desc()).all()
    print("\n===== AUDIT LOGS =====")
    for log in logs:
        user = User.query.get(log.user_id)
        print(f"{log.timestamp} | {user.username if user else 'Unknown'} | {log.action} | {log.module} | {log.details}")
    print("======================")
