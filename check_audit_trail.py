from app import app, db, AuditTrail
from collections import Counter

with app.app_context():
    # Get all audit entries
    audits = AuditTrail.query.all()
    
    print(f'Total audit entries: {len(audits)}')
    print()
    
    # Count by action type
    action_types = Counter([a.action_type for a in audits])
    print('Actions logged:')
    for action, count in sorted(action_types.items()):
        print(f'  {action}: {count}')
    
    print()
    
    # Show recent 10 actions
    recent = AuditTrail.query.order_by(AuditTrail.timestamp.desc()).limit(10).all()
    print('Recent 10 actions:')
    for a in recent:
        print(f'  {a.timestamp} | {a.action_type} | {a.description}')
