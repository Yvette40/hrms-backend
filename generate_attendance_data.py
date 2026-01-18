#!/usr/bin/env python3
"""
Attendance Data Generator
Populates the attendance table with realistic historical data
"""

import os
import sys
from datetime import datetime, timedelta, date
import random

# Add the parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database import db
from app import app
from models import Employee, Attendance, User

def generate_attendance_data(days_back=90):
    """
    Generate realistic attendance data for all employees
    
    Args:
        days_back: Number of days to generate data for (default: 90 days = ~3 months)
    """
    
    with app.app_context():
        # Get all active employees
        employees = Employee.query.filter_by(active=True).all()
        
        if not employees:
            print("❌ No active employees found. Please add employees first.")
            return
        
        print(f"📊 Found {len(employees)} active employees")
        print(f"📅 Generating attendance for last {days_back} days...")
        
        # Get an admin user to record attendance
        admin_user = User.query.filter_by(role='admin').first()
        if not admin_user:
            admin_user = User.query.first()
        
        if not admin_user:
            print("❌ No users found in database")
            return
        
        # Clear existing attendance records (optional - comment out if you want to keep existing data)
        print("🗑️  Clearing existing attendance records...")
        Attendance.query.delete()
        db.session.commit()
        
        # Calculate date range
        end_date = date.today()
        start_date = end_date - timedelta(days=days_back)
        
        total_records = 0
        
        # Generate attendance for each employee
        for employee in employees:
            print(f"👤 Generating attendance for: {employee.name}")
            
            current_date = start_date
            consecutive_absences = 0  # Track consecutive absences for realism
            
            while current_date <= end_date:
                # Skip weekends (Saturday = 5, Sunday = 6)
                if current_date.weekday() >= 5:
                    current_date += timedelta(days=1)
                    continue
                
                # Check if this employee has already joined by this date
                if employee.join_date and current_date < employee.join_date:
                    current_date += timedelta(days=1)
                    continue
                
                # Don't create attendance for future dates
                if current_date > end_date:
                    break
                
                # Determine attendance status with realistic probabilities
                status = determine_status(current_date, consecutive_absences)
                
                # Track consecutive absences
                if status == "Absent":
                    consecutive_absences += 1
                else:
                    consecutive_absences = 0
                
                # Create attendance record
                attendance = Attendance(
                    employee_id=employee.id,
                    date=current_date,
                    status=status,
                    recorded_by=admin_user.id,
                    created_at=datetime.combine(current_date, datetime.min.time())
                )
                
                db.session.add(attendance)
                total_records += 1
                
                current_date += timedelta(days=1)
        
        # Commit all records
        db.session.commit()
        print(f"\n✅ Successfully created {total_records} attendance records!")
        
        # Print summary statistics
        print_attendance_summary()


def determine_status(current_date, consecutive_absences):
    """
    Determine attendance status based on realistic probabilities
    
    Args:
        current_date: The date to generate status for
        consecutive_absences: Number of consecutive absences (to prevent unrealistic patterns)
    
    Returns:
        Status string: "Present", "Late", or "Absent"
    """
    
    # Don't allow more than 3 consecutive absences (unrealistic for most employees)
    if consecutive_absences >= 3:
        # Force present or late if too many consecutive absences
        return "Late" if random.random() < 0.3 else "Present"
    
    # Monday and Friday slightly higher absence rate
    day_of_week = current_date.weekday()
    if day_of_week in [0, 4]:  # Monday or Friday
        absent_probability = 0.08
        late_probability = 0.15
    else:
        absent_probability = 0.05
        late_probability = 0.10
    
    # Generate random number
    rand = random.random()
    
    if rand < absent_probability:
        return "Absent"
    elif rand < (absent_probability + late_probability):
        return "Late"
    else:
        return "Present"


def print_attendance_summary():
    """Print summary statistics of generated attendance data"""
    
    with app.app_context():
        total_records = Attendance.query.count()
        present_records = Attendance.query.filter_by(status="Present").count()
        late_records = Attendance.query.filter_by(status="Late").count()
        absent_records = Attendance.query.filter_by(status="Absent").count()
        
        print("\n" + "="*60)
        print("📊 ATTENDANCE SUMMARY")
        print("="*60)
        print(f"Total Records:     {total_records}")
        print(f"Present:           {present_records} ({present_records/total_records*100:.1f}%)")
        print(f"Late:              {late_records} ({late_records/total_records*100:.1f}%)")
        print(f"Absent:            {absent_records} ({absent_records/total_records*100:.1f}%)")
        print("="*60)
        
        # Show per-employee summary
        employees = Employee.query.filter_by(active=True).all()
        print("\n👥 PER-EMPLOYEE SUMMARY:")
        print("-"*60)
        
        for emp in employees[:10]:  # Show first 10 employees
            emp_attendance = Attendance.query.filter_by(employee_id=emp.id).all()
            if emp_attendance:
                emp_present = len([a for a in emp_attendance if a.status == "Present"])
                emp_total = len(emp_attendance)
                emp_rate = (emp_present / emp_total * 100) if emp_total > 0 else 0
                print(f"{emp.name[:30]:30} | Records: {emp_total:3} | Rate: {emp_rate:.1f}%")
        
        if len(employees) > 10:
            print(f"... and {len(employees) - 10} more employees")
        
        print("-"*60)


def generate_specific_employee_attendance(employee_id, days_back=90):
    """
    Generate attendance data for a specific employee
    
    Args:
        employee_id: ID of the employee
        days_back: Number of days to generate data for
    """
    
    with app.app_context():
        employee = Employee.query.get(employee_id)
        
        if not employee:
            print(f"❌ Employee with ID {employee_id} not found")
            return
        
        print(f"👤 Generating attendance for: {employee.name}")
        
        # Get an admin user
        admin_user = User.query.filter_by(role='admin').first() or User.query.first()
        
        # Clear existing records for this employee
        Attendance.query.filter_by(employee_id=employee_id).delete()
        
        end_date = date.today()
        start_date = end_date - timedelta(days=days_back)
        current_date = start_date
        
        records_created = 0
        consecutive_absences = 0
        
        while current_date <= end_date:
            # Skip weekends
            if current_date.weekday() >= 5:
                current_date += timedelta(days=1)
                continue
            
            # Check join date
            if employee.join_date and current_date < employee.join_date:
                current_date += timedelta(days=1)
                continue
            
            status = determine_status(current_date, consecutive_absences)
            
            if status == "Absent":
                consecutive_absences += 1
            else:
                consecutive_absences = 0
            
            attendance = Attendance(
                employee_id=employee.id,
                date=current_date,
                status=status,
                recorded_by=admin_user.id,
                created_at=datetime.combine(current_date, datetime.min.time())
            )
            
            db.session.add(attendance)
            records_created += 1
            current_date += timedelta(days=1)
        
        db.session.commit()
        print(f"✅ Created {records_created} attendance records for {employee.name}")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Generate attendance data')
    parser.add_argument('--days', type=int, default=90, 
                       help='Number of days to generate data for (default: 90)')
    parser.add_argument('--employee-id', type=int, 
                       help='Generate data for specific employee only')
    parser.add_argument('--clear', action='store_true',
                       help='Clear all existing attendance data first')
    
    args = parser.parse_args()
    
    print("🚀 Attendance Data Generator")
    print("="*60)
    
    if args.employee_id:
        generate_specific_employee_attendance(args.employee_id, args.days)
    else:
        generate_attendance_data(args.days)
    
    print("\n✨ Done! Refresh your frontend to see the data.")
