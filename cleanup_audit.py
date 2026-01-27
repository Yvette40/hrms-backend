# cleanup_audit.py - Clean up noisy audit trail entries
from app import app, db
from models import AuditTrail

print("🧹 Starting Audit Trail Cleanup...")
print("=" * 50)

with app.app_context():
    # Show current state
    total_before = AuditTrail.query.count()
    print(f"📊 Total entries before cleanup: {total_before}")
    
    # Count noisy entries
    noisy_actions = ['VIEW_EMPLOYEES', 'VIEW_DASHBOARD', 'VIEW_PAYROLLS']
    noisy_count = AuditTrail.query.filter(AuditTrail.action_type.in_(noisy_actions)).count()
    print(f"🗑️  Noisy entries to delete: {noisy_count}")
    
    # Ask for confirmation
    if noisy_count > 0:
        confirm = input(f"\n⚠️  Delete {noisy_count} entries? (yes/no): ")
        
        if confirm.lower() == 'yes':
            # Delete noisy entries
            deleted = AuditTrail.query.filter(AuditTrail.action_type.in_(noisy_actions)).delete()
            db.session.commit()
            print(f"\n✅ Deleted {deleted} noisy audit entries!")
            
            # Show final state
            remaining = AuditTrail.query.count()
            print(f"📊 {remaining} important entries remain")
            print(f"🎉 Cleanup complete! Removed {(deleted/total_before)*100:.1f}% of entries")
        else:
            print("\n❌ Cleanup cancelled")
    else:
        print("\n✨ No noisy entries found - audit trail is clean!")

print("=" * 50)
print("Done!")
