#!/usr/bin/env python3
"""
Quick Attendance Data Generator - Simple Version
Just run this to populate attendance data!
"""

import os
import sys
from datetime import datetime, timedelta, date
import random

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database import db
from app import app
from models import Employee, Attendance, User

print("🚀 Quick Attendance Data Generator")
print("="*60)

with app.app_context():
    # Get employees
    employees = Employee.query.filter_by(active=True).all()
    
    if not employees:
        print("❌ No employees found!")
        print("💡 Tip: Add employees first, then run this script.")
        sys.exit(1)
    
    print(f"👥 Found {len(employees)} employees")
    
    # Get admin user
    admin = User.query.filter_by(role='admin').first() or User.query.first()
    
    # Clear old data
    print("🗑️  Clearing old attendance records...")
    Attendance.query.delete()
    db.session.commit()
    
    # Generate 90 days of data
    end_date = date.today()
    start_date = end_date - timedelta(days=90)
    
    print(f"📅 Generating attendance from {start_date} to {end_date}")
    print("⏳ This may take a moment...")
    
    total = 0
    
    for employee in employees:
        current_date = start_date
        
        while current_date <= end_date:
            # Skip weekends
            if current_date.weekday() >= 5:
                current_date += timedelta(days=1)
                continue
            
            # Skip before join date
            if employee.join_date and current_date < employee.join_date:
                current_date += timedelta(days=1)
                continue
            
            # Random status: 85% Present, 10% Late, 5% Absent
            rand = random.random()
            if rand < 0.05:
                status = "Absent"
            elif rand < 0.15:
                status = "Late"
            else:
                status = "Present"
            
            # Create record
            attendance = Attendance(
                employee_id=employee.id,
                date=current_date,
                status=status,
                recorded_by=admin.id,
                created_at=datetime.combine(current_date, datetime.min.time())
            )
            
            db.session.add(attendance)
            total += 1
            
            current_date += timedelta(days=1)
    
    # Save all
    db.session.commit()
    
    # Summary
    present = Attendance.query.filter_by(status="Present").count()
    late = Attendance.query.filter_by(status="Late").count()
    absent = Attendance.query.filter_by(status="Absent").count()
    
    print("\n" + "="*60)
    print("✅ SUCCESS!")
    print("="*60)
    print(f"Total Records:  {total}")
    print(f"Present:        {present} ({present/total*100:.1f}%)")
    print(f"Late:           {late} ({late/total*100:.1f}%)")
    print(f"Absent:         {absent} ({absent/total*100:.1f}%)")
    print("="*60)
    print("\n✨ Refresh your frontend to see the attendance data!")
    print("🌐 Navigate to 'My Attendance' page and you should see records.")
