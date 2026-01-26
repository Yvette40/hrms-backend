from app import app, db, User, Employee, Attendance, Payroll, LeaveRequest
from datetime import datetime, timedelta, time
import random
from faker import Faker

fake = Faker()

# Kenyan departments and positions
DEPARTMENTS = [
    'IT', 'HR', 'Finance', 'Sales', 'Marketing', 
    'Operations', 'Customer Service', 'Logistics',
    'Quality Assurance', 'Research & Development'
]

POSITIONS = {
    'IT': ['Software Developer', 'IT Support', 'Systems Admin', 'Database Admin', 'Network Engineer'],
    'HR': ['HR Officer', 'Recruiter', 'HR Manager', 'Training Coordinator'],
    'Finance': ['Accountant', 'Finance Officer', 'Payroll Specialist', 'Auditor'],
    'Sales': ['Sales Rep', 'Sales Manager', 'Account Executive', 'Business Developer'],
    'Marketing': ['Marketing Officer', 'Content Creator', 'Social Media Manager', 'Brand Manager'],
    'Operations': ['Operations Manager', 'Operations Coordinator', 'Process Analyst'],
    'Customer Service': ['Customer Support', 'Call Center Agent', 'Customer Success Manager'],
    'Logistics': ['Logistics Coordinator', 'Supply Chain Manager', 'Warehouse Supervisor'],
    'Quality Assurance': ['QA Analyst', 'QA Manager', 'Test Engineer'],
    'Research & Development': ['Research Analyst', 'R&D Manager', 'Product Developer']
}

LEAVE_TYPES = ['Annual', 'Sick', 'Maternity', 'Paternity', 'Emergency']

def generate_national_id():
    """Generate realistic Kenyan national ID"""
    return f"{random.randint(10000000, 99999999)}"

def generate_phone():
    """Generate Kenyan phone number"""
    prefix = random.choice(['0712', '0722', '0733', '0710', '0720'])
    return f"{prefix}{random.randint(100000, 999999)}"

def calculate_nssf(gross_salary):
    """Calculate NSSF (6% of gross, max 2,160)"""
    nssf = gross_salary * 0.06
    return min(nssf, 2160)

def calculate_nhif(gross_salary):
    """Calculate NHIF based on Kenyan brackets"""
    if gross_salary <= 5999: return 150
    elif gross_salary <= 7999: return 300
    elif gross_salary <= 11999: return 400
    elif gross_salary <= 14999: return 500
    elif gross_salary <= 19999: return 600
    elif gross_salary <= 24999: return 750
    elif gross_salary <= 29999: return 850
    elif gross_salary <= 34999: return 900
    elif gross_salary <= 39999: return 950
    elif gross_salary <= 44999: return 1000
    elif gross_salary <= 49999: return 1100
    elif gross_salary <= 59999: return 1200
    elif gross_salary <= 69999: return 1300
    elif gross_salary <= 79999: return 1400
    elif gross_salary <= 89999: return 1500
    else: return 1700

def calculate_paye(gross_salary, nssf):
    """Calculate PAYE (Kenyan tax brackets)"""
    taxable = gross_salary - nssf
    tax = 0
    
    if taxable <= 24000:
        tax = taxable * 0.10
    elif taxable <= 32333:
        tax = 2400 + (taxable - 24000) * 0.25
    else:
        tax = 2400 + 2083.25 + (taxable - 32333) * 0.30
    
    return max(tax, 0)

def calculate_housing_levy(gross_salary):
    """Calculate Housing Levy (1.5% of gross)"""
    return gross_salary * 0.015

def generate_realistic_time(base_time, variance_minutes=30):
    """Generate realistic check-in/out time with variance"""
    variance = random.randint(-variance_minutes, variance_minutes)
    hour = base_time.hour
    minute = base_time.minute + variance
    
    if minute >= 60:
        hour += 1
        minute -= 60
    elif minute < 0:
        hour -= 1
        minute += 60
    
    return time(hour, minute)

with app.app_context():
    print('=' * 70)
    print('DATABASE EXPANSION - GENERATING 250 EMPLOYEES WITH FULL DATA')
    print('=' * 70)
    
    # Get current counts
    current_employees = Employee.query.count()
    current_users = User.query.count()
    
    print(f'\n📊 Current Status:')
    print(f'   Employees: {current_employees}')
    print(f'   Users: {current_users}')
    
    employees_to_create = 250 - current_employees
    print(f'\n🎯 Target: {employees_to_create} new employees')
    
    if employees_to_create <= 0:
        print('✅ Already have 250+ employees!')
        exit()
    
    print('\n🔄 Generating data...')
    print('-' * 70)
    
    new_employees = []
    new_users = []
    
    # Get existing national IDs to avoid duplicates
    existing_ids = set([e.national_id for e in Employee.query.all()])
    
    # Generate new employees
    for i in range(employees_to_create):
        # Generate unique national ID
        while True:
            national_id = generate_national_id()
            if national_id not in existing_ids:
                existing_ids.add(national_id)
                break
        
        # Random department and position
        dept = random.choice(DEPARTMENTS)
        position = random.choice(POSITIONS[dept])
        
        # Salary based on position level
        if 'Manager' in position or 'Director' in position:
            base_salary = random.randint(80000, 150000)
        elif 'Coordinator' in position or 'Specialist' in position:
            base_salary = random.randint(50000, 80000)
        else:
            base_salary = random.randint(30000, 60000)
        
        # Create employee
        employee = Employee(
            name=fake.name(),
            national_id=national_id,
            base_salary=base_salary,
            department=dept,
            position=position,
            email=fake.email(),
            phone_number=generate_phone(),
            join_date=(datetime.now() - timedelta(days=random.randint(30, 1095))).date(),
            leave_balance=random.randint(15, 21),
            address=fake.address()[:200],
            emergency_name=fake.name(),
            emergency_contact=generate_phone(),
            active=True
        )
        
        db.session.add(employee)
        db.session.flush()
        
        # Create user account (70% of employees get accounts)
        if random.random() < 0.7:
            username = f"emp_{employee.id}"
            user = User(
                username=username,
                role='Employee',
                email=employee.email,
                phone=employee.phone_number,
                is_active=True
            )
            user.set_password('employee123')
            
            db.session.add(user)
            db.session.flush()
            
            # Link employee to user
            employee.user_id = user.id
            new_users.append(user)
        
        new_employees.append(employee)
        
        if (i + 1) % 50 == 0:
            print(f'   Created {i + 1}/{employees_to_create} employees...')
    
    db.session.commit()
    print(f'\n✅ Created {len(new_employees)} employees')
    print(f'✅ Created {len(new_users)} user accounts')
    
    # Generate biometric attendance data (last 90 days)
    print('\n📅 Generating attendance data (last 90 days)...')
    print('-' * 70)
    
    all_employees = Employee.query.filter_by(active=True).all()
    start_date = datetime.now().date() - timedelta(days=90)
    end_date = datetime.now().date()
    
    attendance_records = []
    current_date = start_date
    
    while current_date <= end_date:
        # Skip weekends
        if current_date.weekday() < 5:
            for employee in all_employees:
                # 85% attendance rate
                if random.random() < 0.85:
                    # Generate realistic check-in time (8:00 AM ± 30 min)
                    check_in = generate_realistic_time(time(8, 0), 30)
                    
                    # Generate check-out time (5:00 PM ± 45 min)
                    check_out = generate_realistic_time(time(17, 0), 45)
                    
                    # Calculate hours worked
                    check_in_dt = datetime.combine(current_date, check_in)
                    check_out_dt = datetime.combine(current_date, check_out)
                    hours_worked = (check_out_dt - check_in_dt).seconds / 3600
                    
                    # Determine status
                    if check_in.hour >= 9:
                        status = 'Late'
                    else:
                        status = 'Present'
                    
                    attendance = Attendance(
                        employee_id=employee.id,
                        date=current_date,
                        status=status,
                        check_in_time=check_in.strftime('%H:%M'),
                        check_out_time=check_out.strftime('%H:%M'),
                        hours_worked=round(hours_worked, 2),
                        notes='Biometric clock'
                    )
                    attendance_records.append(attendance)
                else:
                    attendance = Attendance(
                        employee_id=employee.id,
                        date=current_date,
                        status='Absent'
                    )
                    attendance_records.append(attendance)
        
        current_date += timedelta(days=1)
    
    # Bulk insert attendance
    db.session.bulk_save_objects(attendance_records)
    db.session.commit()
    print(f'✅ Generated {len(attendance_records)} attendance records')
    
    # Generate payroll records (last 3 months)
    print('\n💰 Generating payroll data (last 3 months)...')
    print('-' * 70)
    
    payroll_records = []
    
    for month_offset in range(3):
        period_end = datetime.now().date() - timedelta(days=month_offset * 30)
        period_start = period_end - timedelta(days=30)
        
        for employee in all_employees:
            gross_salary = employee.base_salary
            
            # Calculate deductions
            nssf = calculate_nssf(gross_salary)
            nhif = calculate_nhif(gross_salary)
            paye = calculate_paye(gross_salary, nssf)
            housing_levy = calculate_housing_levy(gross_salary)
            total_deductions = nssf + nhif + paye + housing_levy
            net_salary = gross_salary - total_deductions
            
            # Count attendance days
            attendance_days = Attendance.query.filter(
                Attendance.employee_id == employee.id,
                Attendance.date >= period_start,
                Attendance.date <= period_end,
                Attendance.status.in_(['Present', 'Late'])
            ).count()
            
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
                status=random.choice(['Approved', 'Approved', 'Approved', 'Pending']),
                payment_date=period_end + timedelta(days=5)
            )
            payroll_records.append(payroll)
    
    db.session.bulk_save_objects(payroll_records)
    db.session.commit()
    print(f'✅ Generated {len(payroll_records)} payroll records')
    
    # Generate leave requests
    print('\n🏖️  Generating leave requests...')
    print('-' * 70)
    
    leave_records = []
    
    for employee in all_employees:
        num_leaves = random.randint(2, 5)
        
        for _ in range(num_leaves):
            start_date = fake.date_between(start_date='-90d', end_date='today')
            days = random.randint(1, 10)
            end_date = start_date + timedelta(days=days)
            
            leave = LeaveRequest(
                employee_id=employee.id,
                start_date=start_date,
                end_date=end_date,
                leave_type=random.choice(LEAVE_TYPES),
                reason=fake.sentence(),
                days_requested=days,
                status=random.choice(['Approved', 'Approved', 'Pending', 'Rejected']),
                requested_at=datetime.now() - timedelta(days=random.randint(1, 90))
            )
            leave_records.append(leave)
    
    db.session.bulk_save_objects(leave_records)
    db.session.commit()
    print(f'✅ Generated {len(leave_records)} leave requests')
    
    # Final stats
    print('\n' + '=' * 70)
    print('DATABASE EXPANSION COMPLETE!')
    print('=' * 70)
    print(f'\n📊 Final Counts:')
    print(f'   Employees: {Employee.query.count()}')
    print(f'   Users: {User.query.count()}')
    print(f'   Attendance: {Attendance.query.count()}')
    print(f'   Payroll: {Payroll.query.count()}')
    print(f'   Leave Requests: {LeaveRequest.query.count()}')
    print('\n✅ All data generated successfully!')
    print('=' * 70)