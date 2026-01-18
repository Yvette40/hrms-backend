#!/usr/bin/env python3
"""
Leave Records Data Generator
Generates realistic leave requests with various statuses and types
"""

import sys
import os
from datetime import datetime, date, timedelta
import random

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database import db
from app import app
from models import Employee, LeaveRequest, User

# Leave types and their typical durations
LEAVE_TYPES = {
    'Annual': (3, 14),  # Annual leave: 3-14 days
    'Sick': (1, 5),     # Sick leave: 1-5 days
    'Maternity': (90, 90),  # Maternity: 90 days
    'Paternity': (14, 14),  # Paternity: 14 days
    'Unpaid': (2, 10),  # Unpaid leave: 2-10 days
    'Emergency': (1, 3),  # Emergency: 1-3 days
}

# Typical reasons for each leave type
LEAVE_REASONS = {
    'Annual': [
        'Family vacation',
        'Personal matters',
        'Rest and relaxation',
        'Wedding attendance',
        'Travel plans',
        'Holiday break',
        'Family reunion',
    ],
    'Sick': [
        'Medical appointment',
        'Flu symptoms',
        'Doctor consultation',
        'Health checkup',
        'Recovery period',
        'Medical treatment',
    ],
    'Maternity': [
        'Maternity leave',
        'Childbirth',
        'Prenatal care',
    ],
    'Paternity': [
        'Paternity leave',
        'Supporting spouse',
        'New baby care',
    ],
    'Unpaid': [
        'Personal emergency',
        'Extended family matters',
        'Additional leave required',
    ],
    'Emergency': [
        'Family emergency',
        'Urgent personal matter',
        'Unexpected situation',
    ]
}

# Rejection reasons (for rejected leaves)
REJECTION_REASONS = [
    'Insufficient leave balance',
    'Critical period for the department',
    'Multiple team members on leave during same period',
    'Advance notice period not met',
    'Peak business period',
    'Staffing constraints',
]


def generate_leave_records(months_back=12, clear_existing=True):
    """
    Generate historical leave requests
    
    Args:
        months_back: Number of months to generate data for (default: 12)
        clear_existing: Whether to clear existing leave records
    """
    
    with app.app_context():
        print("🏖️ LEAVE RECORDS GENERATOR")
        print("="*60)
        
        # Get employees and approvers
        employees = Employee.query.filter_by(active=True).all()
        
        if not employees:
            print("❌ No active employees found!")
            return
        
        print(f"👥 Found {len(employees)} active employees")
        
        # Get approvers (admin and HR)
        approvers = User.query.filter(
            (User.role == 'admin') | (User.role == 'hr')
        ).all()
        
        if not approvers:
            approvers = [User.query.first()]
        
        # Clear existing leave requests if requested
        if clear_existing:
            print("🗑️  Clearing existing leave records...")
            LeaveRequest.query.delete()
            db.session.commit()
        
        print(f"📅 Generating leave requests for last {months_back} months...")
        
        total_records = 0
        stats = {
            'Approved': 0,
            'Pending': 0,
            'Rejected': 0,
        }
        type_stats = {leave_type: 0 for leave_type in LEAVE_TYPES.keys()}
        
        # Calculate date range
        end_date = date.today()
        start_date = end_date - timedelta(days=months_back * 30)
        
        # Generate leave requests for each employee
        for employee in employees:
            # Each employee gets 2-8 leave requests over the period
            num_requests = random.randint(2, 8)
            
            print(f"👤 Generating {num_requests} leave requests for {employee.name}...")
            
            for _ in range(num_requests):
                # Random leave type (weighted probabilities)
                leave_type_choices = [
                    'Annual', 'Annual', 'Annual', 'Annual',  # 40% annual
                    'Sick', 'Sick', 'Sick',  # 30% sick
                    'Emergency', 'Emergency',  # 20% emergency
                    'Unpaid',  # 10% unpaid
                ]
                
                # Special cases for maternity/paternity (rare)
                if random.random() < 0.05:  # 5% chance
                    leave_type = random.choice(['Maternity', 'Paternity'])
                else:
                    leave_type = random.choice(leave_type_choices)
                
                # Get duration range for this leave type
                min_days, max_days = LEAVE_TYPES[leave_type]
                days = random.randint(min_days, max_days)
                
                # Random start date within the period
                days_offset = random.randint(0, months_back * 30 - days)
                leave_start = start_date + timedelta(days=days_offset)
                
                # Check if employee had joined by then
                if employee.join_date and leave_start < employee.join_date:
                    leave_start = employee.join_date + timedelta(days=random.randint(30, 90))
                
                leave_end = leave_start + timedelta(days=days - 1)
                
                # Ensure it's not in the future
                if leave_end > end_date:
                    leave_end = end_date
                    leave_start = leave_end - timedelta(days=days - 1)
                
                # Random reason
                reason = random.choice(LEAVE_REASONS[leave_type])
                
                # Determine status based on how old the request is
                days_since_request = (end_date - leave_end).days
                
                if days_since_request > 30:  # Old requests are decided
                    # 85% approved, 15% rejected for old requests
                    if random.random() < 0.85:
                        status = 'Approved'
                        approver = random.choice(approvers)
                        approved_at = leave_start - timedelta(days=random.randint(3, 10))
                        rejection_reason = None
                    else:
                        status = 'Rejected'
                        approver = random.choice(approvers)
                        approved_at = leave_start - timedelta(days=random.randint(3, 10))
                        rejection_reason = random.choice(REJECTION_REASONS)
                elif days_since_request > 7:  # Recent requests - mostly decided
                    if random.random() < 0.70:
                        status = 'Approved'
                        approver = random.choice(approvers)
                        approved_at = datetime.now() - timedelta(days=random.randint(1, 7))
                        rejection_reason = None
                    elif random.random() < 0.15:
                        status = 'Rejected'
                        approver = random.choice(approvers)
                        approved_at = datetime.now() - timedelta(days=random.randint(1, 7))
                        rejection_reason = random.choice(REJECTION_REASONS)
                    else:
                        status = 'Pending'
                        approver = None
                        approved_at = None
                        rejection_reason = None
                else:  # Very recent - mostly pending
                    if random.random() < 0.30:
                        status = 'Approved'
                        approver = random.choice(approvers)
                        approved_at = datetime.now() - timedelta(hours=random.randint(2, 48))
                        rejection_reason = None
                    else:
                        status = 'Pending'
                        approver = None
                        approved_at = None
                        rejection_reason = None
                
                # Create requested_at timestamp
                requested_at = leave_start - timedelta(days=random.randint(10, 30))
                
                # Create leave request
                leave_request = LeaveRequest(
                    employee_id=employee.id,
                    start_date=leave_start,
                    end_date=leave_end,
                    leave_type=leave_type,
                    reason=reason,
                    days_requested=days,
                    status=status,
                    requested_at=requested_at,
                    approved_by=approver.id if approver else None,
                    approved_at=approved_at,
                    rejection_reason=rejection_reason
                )
                
                db.session.add(leave_request)
                total_records += 1
                stats[status] += 1
                type_stats[leave_type] += 1
        
        # Commit all records
        db.session.commit()
        
        print("\n" + "="*60)
        print("✅ LEAVE RECORDS GENERATION COMPLETE!")
        print("="*60)
        print(f"Total Records:  {total_records}")
        print(f"\nBy Status:")
        print(f"  Approved:     {stats['Approved']} ({stats['Approved']/total_records*100:.1f}%)")
        print(f"  Pending:      {stats['Pending']} ({stats['Pending']/total_records*100:.1f}%)")
        print(f"  Rejected:     {stats['Rejected']} ({stats['Rejected']/total_records*100:.1f}%)")
        print(f"\nBy Type:")
        for leave_type, count in type_stats.items():
            if count > 0:
                print(f"  {leave_type:12} {count} ({count/total_records*100:.1f}%)")
        print("="*60)
        
        # Show sample leave requests
        print_sample_leave_requests()


def print_sample_leave_requests():
    """Print sample leave request data"""
    
    with app.app_context():
        print("\n📋 SAMPLE LEAVE REQUESTS:")
        print("-"*60)
        
        # Show mix of different statuses
        for status in ['Approved', 'Pending', 'Rejected']:
            sample = LeaveRequest.query.filter_by(status=status).first()
            
            if sample:
                employee = Employee.query.get(sample.employee_id)
                
                print(f"\n{status.upper()}: {employee.name if employee else 'Unknown'}")
                print(f"Type:   {sample.leave_type}")
                print(f"Dates:  {sample.start_date} to {sample.end_date}")
                print(f"Days:   {sample.days_requested}")
                print(f"Reason: {sample.reason}")
                print(f"Requested: {sample.requested_at.date()}")
                if sample.approved_at:
                    print(f"Decided: {sample.approved_at.date()}")
                if sample.rejection_reason:
                    print(f"Rejection: {sample.rejection_reason}")
                print("-"*60)


def generate_specific_employee_leaves(employee_id, num_requests=5):
    """
    Generate leave requests for a specific employee
    
    Args:
        employee_id: ID of the employee
        num_requests: Number of leave requests to generate
    """
    
    with app.app_context():
        employee = Employee.query.get(employee_id)
        
        if not employee:
            print(f"❌ Employee with ID {employee_id} not found")
            return
        
        print(f"👤 Generating {num_requests} leave requests for: {employee.name}")
        
        # Get approvers
        approvers = User.query.filter(
            (User.role == 'admin') | (User.role == 'hr')
        ).all()
        
        if not approvers:
            approvers = [User.query.first()]
        
        # Clear existing for this employee
        LeaveRequest.query.filter_by(employee_id=employee_id).delete()
        
        for _ in range(num_requests):
            # Random leave type
            leave_type = random.choice(list(LEAVE_TYPES.keys()))
            min_days, max_days = LEAVE_TYPES[leave_type]
            days = random.randint(min_days, max_days)
            
            # Date range
            days_back = random.randint(30, 365)
            leave_start = date.today() - timedelta(days=days_back)
            leave_end = leave_start + timedelta(days=days - 1)
            
            # Status (mix)
            status = random.choice(['Approved', 'Approved', 'Pending', 'Rejected'])
            
            if status != 'Pending':
                approver = random.choice(approvers)
                approved_at = leave_start - timedelta(days=2)
                rejection_reason = random.choice(REJECTION_REASONS) if status == 'Rejected' else None
            else:
                approver = None
                approved_at = None
                rejection_reason = None
            
            leave_request = LeaveRequest(
                employee_id=employee.id,
                start_date=leave_start,
                end_date=leave_end,
                leave_type=leave_type,
                reason=random.choice(LEAVE_REASONS[leave_type]),
                days_requested=days,
                status=status,
                requested_at=leave_start - timedelta(days=random.randint(10, 30)),
                approved_by=approver.id if approver else None,
                approved_at=approved_at,
                rejection_reason=rejection_reason
            )
            
            db.session.add(leave_request)
        
        db.session.commit()
        print(f"✅ Created {num_requests} leave requests for {employee.name}")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Generate leave request data')
    parser.add_argument('--months', type=int, default=12,
                       help='Number of months to generate data for (default: 12)')
    parser.add_argument('--employee-id', type=int,
                       help='Generate for specific employee only')
    parser.add_argument('--num-requests', type=int, default=5,
                       help='Number of requests per employee (default: 5)')
    parser.add_argument('--keep-existing', action='store_true',
                       help='Keep existing leave records (default: clear)')
    
    args = parser.parse_args()
    
    print("🚀 Leave Records Generator")
    print("="*60)
    
    if args.employee_id:
        generate_specific_employee_leaves(args.employee_id, args.num_requests)
    else:
        generate_leave_records(
            months_back=args.months,
            clear_existing=not args.keep_existing
        )
    
    print("\n✨ Done! Refresh your frontend to see leave records.")
