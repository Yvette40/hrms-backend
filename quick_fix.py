from app import app, db
from models import User, Employee
from datetime import date

print("Starting fix...")

with app.app_context():
    # Fix jmwangi
    user = User.query.get(89)
    emp = Employee.query.filter_by(email='john.mwangi@glimmer.com').first()
    if user and emp and emp.user_id != 89:
        emp.user_id = 89
        print("✅ Fixed jmwangi")
    
    # Create system user profiles
    system = [
        (1, 'admin', 'System Administrator', 'ADMIN001'),
        (2, 'hr_officer', 'HR Officer', 'HR001'),
        (3, 'dept_manager', 'Department Manager', 'MGR001'),
        (4, 'employee', 'General Employee', 'EMP000'),
    ]
    
    for uid, name, fullname, nid in system:
        u = User.query.get(uid)
        if u and not Employee.query.filter_by(user_id=uid).first():
            e = Employee(
                name=fullname,
                national_id=nid,
                department='Administration',
                position='Staff',
                email=f'{name}@company.com',
                phone_number='+254700000000',
                base_salary=80000,
                join_date=date.today(),
                user_id=uid,
                active=True,
                leave_balance=21
            )
            db.session.add(e)
            print(f"✅ Created {name}")
    
    db.session.commit()
    print("✅ All done!")