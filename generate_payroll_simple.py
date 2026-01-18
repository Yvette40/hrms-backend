#!/usr/bin/env python3
"""
Payroll & Payslips Data Generator (No Dependencies Version)
Generates historical payroll records with realistic Kenyan tax calculations
"""

import sys
import os
from datetime import datetime, date, timedelta
from calendar import monthrange
import random

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database import db
from app import app
from models import Employee, Payroll, User, Attendance

def add_months(source_date, months):
    """Add months to a date without external dependencies"""
    month = source_date.month - 1 + months
    year = source_date.year + month // 12
    month = month % 12 + 1
    day = min(source_date.day, monthrange(year, month)[1])
    return date(year, month, day)

def get_month_period(months_back):
    """Get first and last day of a month X months ago"""
    today = date.today()
    target_date = add_months(today, -months_back)
    
    # First day of month
    period_start = target_date.replace(day=1)
    
    # Last day of month
    last_day = monthrange(target_date.year, target_date.month)[1]
    period_end = target_date.replace(day=last_day)
    
    return period_start, period_end

def calculate_nssf(gross_salary):
    """Calculate NSSF deduction (6% capped at KES 1,080)"""
    nssf = gross_salary * 0.06
    return min(nssf, 1080)

def calculate_nhif(gross_salary):
    """Calculate NHIF deduction based on Kenyan rates"""
    if gross_salary <= 5999:
        return 150
    elif gross_salary <= 7999:
        return 300
    elif gross_salary <= 11999:
        return 400
    elif gross_salary <= 14999:
        return 500
    elif gross_salary <= 19999:
        return 600
    elif gross_salary <= 24999:
        return 750
    elif gross_salary <= 29999:
        return 850
    elif gross_salary <= 34999:
        return 900
    elif gross_salary <= 39999:
        return 950
    elif gross_salary <= 44999:
        return 1000
    elif gross_salary <= 49999:
        return 1100
    elif gross_salary <= 59999:
        return 1200
    elif gross_salary <= 69999:
        return 1300
    elif gross_salary <= 79999:
        return 1400
    elif gross_salary <= 89999:
        return 1500
    elif gross_salary <= 99999:
        return 1600
    else:
        return 1700

def calculate_paye(gross_salary, nssf):
    """Calculate PAYE (Kenya tax brackets 2024)"""
    taxable_income = gross_salary - nssf
    
    # Personal relief
    personal_relief = 2400
    
    # Tax brackets
    if taxable_income <= 24000:
        tax = taxable_income * 0.10
    elif taxable_income <= 32333:
        tax = 24000 * 0.10 + (taxable_income - 24000) * 0.25
    elif taxable_income <= 500000:
        tax = 24000 * 0.10 + 8333 * 0.25 + (taxable_income - 32333) * 0.30
    elif taxable_income <= 800000:
        tax = 24000 * 0.10 + 8333 * 0.25 + 467667 * 0.30 + (taxable_income - 500000) * 0.325
    else:
        tax = 24000 * 0.10 + 8333 * 0.25 + 467667 * 0.30 + 300000 * 0.325 + (taxable_income - 800000) * 0.35
    
    # Apply personal relief
    paye = max(tax - personal_relief, 0)
    
    return round(paye, 2)

def calculate_housing_levy(gross_salary):
    """Calculate Housing Development Levy (1.5% of gross)"""
    return round(gross_salary * 0.015, 2)

def get_attendance_days(employee_id, period_start, period_end):
    """Get actual attendance days for the period"""
    attendance = Attendance.query.filter(
        Attendance.employee_id == employee_id,
        Attendance.date >= period_start,
        Attendance.date <= period_end,
        Attendance.status == 'Present'
    ).count()
    
    return attendance

def generate_payroll_data(months_back=6, clear_existing=True):
    """
    Generate historical payroll data
    
    Args:
        months_back: Number of months to generate data for (default: 6)
        clear_existing: Whether to clear existing payroll records
    """
    
    with app.app_context():
        print("💰 PAYROLL DATA GENERATOR")
        print("="*60)
        
        # Get employees and users
        employees = Employee.query.filter_by(active=True).all()
        
        if not employees:
            print("❌ No active employees found!")
            return
        
        print(f"👥 Found {len(employees)} active employees")
        
        # Get HR officer and admin for approval workflow
        hr_user = User.query.filter_by(role='hr').first()
        admin_user = User.query.filter_by(role='admin').first()
        
        if not hr_user:
            hr_user = User.query.first()
        if not admin_user:
            admin_user = User.query.first()
        
        # Clear existing payroll if requested
        if clear_existing:
            print("🗑️  Clearing existing payroll records...")
            Payroll.query.delete()
            db.session.commit()
        
        print(f"📅 Generating payroll for last {months_back} months...")
        
        total_records = 0
        total_approved = 0
        total_pending = 0
        
        # Generate payroll for each month
        for month_offset in range(months_back, 0, -1):
            # Calculate period
            period_start, period_end = get_month_period(month_offset)
            
            print(f"\n📆 Processing {period_start.strftime('%B %Y')}...")
            
            # Determine approval status (older months are approved, recent might be pending)
            if month_offset > 1:
                status = 'Approved'
                approved_by = admin_user.id if admin_user else None
                approved_at = period_end + timedelta(days=random.randint(5, 10))
                payment_date = period_end + timedelta(days=random.randint(3, 7))
            else:
                # Most recent month - mix of approved and pending
                if random.random() < 0.7:  # 70% approved
                    status = 'Approved'
                    approved_by = admin_user.id if admin_user else None
                    approved_at = datetime.now() - timedelta(days=random.randint(1, 5))
                    payment_date = date.today() - timedelta(days=random.randint(1, 3))
                else:
                    status = 'Pending'
                    approved_by = None
                    approved_at = None
                    payment_date = None
            
            # Generate payroll for each employee
            for employee in employees:
                # Check if employee had joined by this period
                if employee.join_date and employee.join_date > period_end:
                    continue  # Skip if not yet joined
                
                # Get base salary
                gross_salary = employee.base_salary
                
                # Add random variation (bonus, overtime) - 10% chance
                if random.random() < 0.1:
                    bonus = random.choice([5000, 10000, 15000])
                    gross_salary += bonus
                
                # Calculate deductions
                nssf = calculate_nssf(gross_salary)
                nhif = calculate_nhif(gross_salary)
                paye = calculate_paye(gross_salary, nssf)
                housing_levy = calculate_housing_levy(gross_salary)
                
                total_deductions = nssf + nhif + paye + housing_levy
                net_salary = gross_salary - total_deductions
                
                # Get attendance days
                attendance_days = get_attendance_days(employee.id, period_start, period_end)
                
                # Detect anomaly (e.g., low attendance but full salary)
                expected_days = 22  # Average working days per month
                anomaly_flag = attendance_days < (expected_days * 0.7) and attendance_days > 0
                
                # Payment method
                payment_method = random.choice([
                    'Bank Transfer', 'Bank Transfer', 'Bank Transfer',  # Most common
                    'Mobile Money', 'Cash'
                ])
                
                # Create payroll record
                payroll = Payroll(
                    employee_id=employee.id,
                    period_start=period_start,
                    period_end=period_end,
                    gross_salary=gross_salary,
                    nssf=nssf,
                    nhif=nhif,
                    paye=paye,
                    housing_levy=housing_levy,
                    total_deductions=total_deductions,
                    net_salary=net_salary,
                    attendance_days=attendance_days,
                    anomaly_flag=anomaly_flag,
                    status=status,
                    prepared_by=hr_user.id if hr_user else None,
                    approved_by=approved_by,
                    approved_at=approved_at,
                    payment_date=payment_date,
                    payment_method=payment_method if status == 'Approved' else None,
                    created_at=period_end + timedelta(days=1)  # Created day after period
                )
                
                db.session.add(payroll)
                total_records += 1
                
                if status == 'Approved':
                    total_approved += 1
                else:
                    total_pending += 1
        
        # Commit all records
        db.session.commit()
        
        print("\n" + "="*60)
        print("✅ PAYROLL GENERATION COMPLETE!")
        print("="*60)
        print(f"Total Records:  {total_records}")
        print(f"Approved:       {total_approved}")
        print(f"Pending:        {total_pending}")
        print("="*60)
        
        # Show sample payslips
        print_sample_payslips()


def print_sample_payslips():
    """Print sample payslip data"""
    
    with app.app_context():
        print("\n📋 SAMPLE PAYSLIPS:")
        print("-"*60)
        
        sample_payrolls = Payroll.query.order_by(
            Payroll.period_end.desc()
        ).limit(5).all()
        
        for payroll in sample_payrolls:
            employee = Employee.query.get(payroll.employee_id)
            
            print(f"\n{employee.name if employee else 'Unknown'}")
            print(f"Period: {payroll.period_start} to {payroll.period_end}")
            print(f"Gross:  KES {payroll.gross_salary:,.2f}")
            print(f"NSSF:   KES {payroll.nssf:,.2f}")
            print(f"NHIF:   KES {payroll.nhif:,.2f}")
            print(f"PAYE:   KES {payroll.paye:,.2f}")
            print(f"H.Levy: KES {payroll.housing_levy:,.2f}")
            print(f"Total Deductions: KES {payroll.total_deductions:,.2f}")
            print(f"NET PAY: KES {payroll.net_salary:,.2f}")
            print(f"Status: {payroll.status}")
            print(f"Days:   {payroll.attendance_days}")
            if payroll.anomaly_flag:
                print("⚠️  ANOMALY DETECTED")
            print("-"*60)


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Generate payroll data')
    parser.add_argument('--months', type=int, default=6,
                       help='Number of months to generate data for (default: 6)')
    parser.add_argument('--keep-existing', action='store_true',
                       help='Keep existing payroll records (default: clear)')
    
    args = parser.parse_args()
    
    print("🚀 Payroll & Payslips Generator (No Dependencies)")
    print("="*60)
    
    generate_payroll_data(
        months_back=args.months,
        clear_existing=not args.keep_existing
    )
    
    print("\n✨ Done! Refresh your frontend to see payslips.")
