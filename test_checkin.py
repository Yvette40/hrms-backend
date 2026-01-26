from app import app, db, User, Employee, Attendance
from datetime import datetime, time

with app.app_context():
    # Find mjoroge's employee record
    user = User.query.filter_by(username='mjoroge').first()
    
    if user and user.employee_profile:
        employee = user.employee_profile[0] if user.employee_profile else None
        
        if employee:
            # Create today's attendance
            today = datetime.now().date()
            
            # Check if already checked in today
            existing = Attendance.query.filter_by(
                employee_id=employee.id,
                date=today
            ).first()
            
            if existing:
                print(f'Already checked in today at {existing.check_in_time}')
            else:
                attendance = Attendance(
                    employee_id=employee.id,
                    date=today,
                    status='Present',
                    check_in_time='08:15',
                    notes='Test check-in'
                )
                db.session.add(attendance)
                db.session.commit()
                print(f'✅ Checked in {employee.name} at 08:15')
                print(f'   Employee ID: {employee.id}')
    else:
        print('❌ Employee profile not found for mjoroge')
