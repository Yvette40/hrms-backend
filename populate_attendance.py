from datetime import datetime, timedelta, date
import random
from database import db
from app import app
from models import Employee, Attendance, User

with app.app_context():
    # Get employees and admin
    employees = Employee.query.filter_by(active=True).all()
    admin = User.query.first()
    
    # Clear old data
    Attendance.query.delete()
    db.session.commit()
    
    # Generate 90 days
    end_date = date.today()
    start_date = end_date - timedelta(days=90)
    
    for employee in employees:
        current_date = start_date
        
        while current_date <= end_date:
            # Skip weekends
            if current_date.weekday() < 5:
                # Skip if before join date
                if not employee.join_date or current_date >= employee.join_date:
                    # Random status
                    rand = random.random()
                    status = 'Absent' if rand < 0.05 else ('Late' if rand < 0.15 else 'Present')
                    
                    # Create record
                    db.session.add(Attendance(
                        employee_id=employee.id,
                        date=current_date,
                        status=status,
                        recorded_by=admin.id
                    ))
            
            current_date += timedelta(days=1)
    
    db.session.commit()
    print(f"✅ Created {Attendance.query.count()} attendance records!")