from app import app, db, Attendance
from datetime import datetime

with app.app_context():
    today = datetime.now().date()
    
    today_records = Attendance.query.filter_by(date=today).all()
    
    print(f'Attendance records for TODAY ({today}):')
    print('=' * 60)
    
    if today_records:
        for att in today_records:
            print(f'Employee ID: {att.employee_id}')
            print(f'Check-in: {att.check_in_time}')
            print(f'Check-out: {att.check_out_time}')
            print(f'Status: {att.status}')
            print('-' * 60)
    else:
        print('NO attendance records for today yet!')
