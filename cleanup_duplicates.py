from app import app, db, Attendance
from datetime import datetime

with app.app_context():
    today = datetime.now().date()
    
    # Delete all records with Status='Leave' and no check-in time
    duplicates = Attendance.query.filter_by(
        date=today,
        status='Leave',
        check_in_time=None
    ).all()
    
    print(f'Found {len(duplicates)} duplicate Leave records')
    
    for dup in duplicates:
        db.session.delete(dup)
    
    db.session.commit()
    print('✅ Duplicates deleted!')
    
    # Show remaining records
    remaining = Attendance.query.filter_by(date=today).all()
    print(f'\n📊 Remaining attendance records for today: {len(remaining)}')
    for att in remaining:
        print(f'  - Employee {att.employee_id}: {att.status} (In: {att.check_in_time})')
