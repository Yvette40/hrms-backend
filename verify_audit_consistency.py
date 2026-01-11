# verify_audit_consistency.py

from app import app, db
from models import AuditTrail, Employee
from datetime import datetime

def verify_audit_consistency():
    print("Running backend audit consistency check...\n")

    audit_entries = AuditTrail.query.all()
    employee_ids = [e.id for e in Employee.query.all()]

    duplicate_check = {}
    missing_user_ids = []
    missing_modules = []
    invalid_timestamps = []
    duplicates = []

    for entry in audit_entries:
        # Key helps detect duplicate log entries (same action + same user + same timestamp)
        key = (entry.action, entry.user_id, entry.timestamp)

        if key in duplicate_check:
            duplicates.append(entry)
        else:
            duplicate_check[key] = True

        if not entry.user_id:
            missing_user_ids.append(entry)

        if not entry.module or entry.module.strip() == "":
            missing_modules.append(entry)

        if not entry.timestamp or not isinstance(entry.timestamp, datetime):
            invalid_timestamps.append(entry)

    print(f"✅ Total audit entries: {len(audit_entries)}")
    print(f"🧩 Employee records found: {len(employee_ids)}")
    print(f"🔁 Duplicate audit entries: {len(duplicates)}")
    print(f"🚫 Missing user_id: {len(missing_user_ids)}")
    print(f"⚠️ Missing module name: {len(missing_modules)}")
    print(f"⏰ Invalid timestamps: {len(invalid_timestamps)}")

    if len(duplicates) == 0 and len(missing_user_ids) == 0 and len(missing_modules) == 0 and len(invalid_timestamps) == 0:
        print("\n🎯 All checks passed! Audit logging is consistent.")
    else:
        print("\n❌ Issues detected — please review the above counts.")
        print("   Fix missing data or remove duplicate trigger/backend logs.")

if __name__ == "__main__":
    with app.app_context():
        verify_audit_consistency()
