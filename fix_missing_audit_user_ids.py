# fix_missing_audit_user_ids.py

from app import app, db
from models import AuditTrail
from sqlalchemy import or_

def fix_missing_user_ids(default_user_id=1):
    print("🔧 Running audit log repair for missing or invalid user_id entries...\n")

    # Find entries where user_id is NULL, 0, empty string, or the text 'None'
    missing_entries = AuditTrail.query.filter(
        or_(
            AuditTrail.user_id == None,
            AuditTrail.user_id == 0,
            AuditTrail.user_id == '',
        )
    ).all()

    if not missing_entries:
        print("✅ No missing or invalid user_id entries found. All logs are complete.")
        return

    print(f"Found {len(missing_entries)} audit logs with missing or invalid user_id.")
    print(f"Assigning default user_id = {default_user_id}...\n")

    for entry in missing_entries:
        entry.user_id = default_user_id

    db.session.commit()
    print(f"✅ Successfully updated {len(missing_entries)} audit entries.\n")
    print("🎯 All audit logs now have valid user_id values.")

if __name__ == "__main__":
    with app.app_context():
        fix_missing_user_ids(default_user_id=1)
