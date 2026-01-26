from app import app, db, Attendance, Employee
from datetime import datetime

with app.app_context():
    today = datetime.now().date()
    
    # Get today's records with both check-in and check-out
    complete_records = Attendance.query.filter(
        Attendance.date == today,
        Attendance.check_in_time != None,
        Attendance.check_out_time != None
    ).all()
    
    print(f'Complete attendance records for today ({today}):')
    print('=' * 80)
    
    for record in complete_records:
        emp = Employee.query.get(record.employee_id)
        print(f'Employee: {emp.name}')
        print(f'  Check-in:  {record.check_in_time}')
        print(f'  Check-out: {record.check_out_time}')
        print(f'  Hours:     {record.hours_worked}')
        print(f'  Status:    {record.status}')
        print('-' * 80)
    
    if not complete_records:
        print('No completed check-ins/check-outs yet today')
        print('\nRecords with only check-in:')
        checkin_only = Attendance.query.filter(
            Attendance.date == today,
            Attendance.check_in_time != None,
            Attendance.check_out_time == None
        ).all()
        for record in checkin_only:
            emp = Employee.query.get(record.employee_id)
            print(f'  {emp.name}: Checked in at {record.check_in_time}, not yet checked out')
