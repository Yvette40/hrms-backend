"""
Update Employee Data - Flask App Version
Run this from your project directory where app.py and models.py are located
Usage: python update_employee_data.py
"""

try:
    from app import app, db
    from models import Employee
except ImportError:
    print("❌ Error: Cannot import app modules.")
    print("Make sure this script is in your project directory with app.py and models.py")
    import sys
    sys.exit(1)

# Employee updates mapping (national_id -> new data)
EMPLOYEE_UPDATES = {
    '12345678': {
        'department': 'Engineering',
        'position': 'Software Engineer',
        'email': 'john.mwangi@glimmer.com',
        'phone_number': '+254712345678'
    },
    '23456789': {
        'department': 'Finance',
        'position': 'Accountant',
        'email': 'mary.wanjiku@glimmer.com',
        'phone_number': '+254723456789'
    },
    '34567890': {
        'department': 'Sales',
        'position': 'Sales Manager',
        'email': 'peter.omondi@glimmer.com',
        'phone_number': '+254734567890'
    },
    '45678901': {
        'department': 'Marketing',
        'position': 'Marketing Officer',
        'email': 'jane.akinyi@glimmer.com',
        'phone_number': '+254745678901'
    },
    '56789012': {
        'department': 'Engineering',
        'position': 'Senior Developer',
        'email': 'david.kamau@glimmer.com',
        'phone_number': '+254756789012'
    },
    '67890123': {
        'department': 'HR',
        'position': 'HR Assistant',
        'email': 'grace.njeri@glimmer.com',
        'phone_number': '+254767890123'
    },
    '78901234': {
        'department': 'Operations',
        'position': 'Operations Manager',
        'email': 'james.otieno@glimmer.com',
        'phone_number': '+254778901234'
    },
    '89012345': {
        'department': 'Finance',
        'position': 'Financial Analyst',
        'email': 'lucy.chebet@glimmer.com',
        'phone_number': '+254789012345'
    },
    '90123456': {
        'department': 'Sales',
        'position': 'Sales Executive',
        'email': 'samuel.kipchoge@glimmer.com',
        'phone_number': '+254790123456'
    },
    '01234567': {
        'department': 'Admin',
        'position': 'Office Administrator',
        'email': 'rose.wambui@glimmer.com',
        'phone_number': '+254701234567'
    },
    '11234568': {
        'department': 'IT',
        'position': 'IT Support Specialist',
        'email': 'patrick.mutua@glimmer.com',
        'phone_number': '+254711234568'
    },
    '21234569': {
        'department': 'Customer Service',
        'position': 'Customer Service Representative',
        'email': 'susan.nyambura@glimmer.com',
        'phone_number': '+254721234569'
    },
    '31234560': {
        'department': 'Logistics',
        'position': 'Logistics Coordinator',
        'email': 'michael.ochieng@glimmer.com',
        'phone_number': '+254731234560'
    },
    '41234561': {
        'department': 'Legal',
        'position': 'Legal Officer',
        'email': 'ann.muthoni@glimmer.com',
        'phone_number': '+254741234561'
    },
    '51234562': {
        'department': 'Procurement',
        'position': 'Procurement Officer',
        'email': 'robert.kariuki@glimmer.com',
        'phone_number': '+254751234562'
    }
}

def update_employees():
    """Update employee records with department, position, and contact info"""
    
    print("\n" + "="*80)
    print("UPDATING EMPLOYEE DATA")
    print("="*80 + "\n")
    
    with app.app_context():
        updated_count = 0
        skipped_count = 0
        
        for national_id, update_data in EMPLOYEE_UPDATES.items():
            employee = Employee.query.filter_by(national_id=national_id).first()
            
            if not employee:
                print(f"⚠️  Employee with ID {national_id} not found - skipping")
                skipped_count += 1
                continue
            
            # Update fields
            employee.department = update_data['department']
            employee.position = update_data['position']
            employee.email = update_data['email']
            employee.phone_number = update_data['phone_number']
            
            print(f"✅ Updated: {employee.name:<25} → {employee.department:<15} | {employee.position}")
            updated_count += 1
        
        # Commit all changes
        db.session.commit()
        
        print("\n" + "="*80)
        print(f"✅ Successfully updated {updated_count} employees")
        if skipped_count > 0:
            print(f"⚠️  Skipped {skipped_count} employees (not found)")
        print("="*80 + "\n")
        
        # Show summary by department
        print("Department Summary:")
        print("-"*80)
        
        from sqlalchemy import func
        dept_counts = db.session.query(
            Employee.department,
            func.count(Employee.id)
        ).group_by(Employee.department).all()
        
        for dept, count in dept_counts:
            print(f"  {dept:<25} {count:>3} employees")
        
        print("-"*80)
        
        # Show sample employees
        print("\nSample Updated Employees:")
        print("-"*80)
        
        sample_employees = Employee.query.limit(10).all()
        for emp in sample_employees:
            print(f"  {emp.name:<20} | {emp.department:<15} | {emp.position:<25} | {emp.email}")
        
        print("\n" + "="*80)
        print("✅ UPDATE COMPLETE!")
        print("="*80)

if __name__ == "__main__":
    print("\n⚠️  This will update existing employee records with:")
    print("   • Department assignments")
    print("   • Position titles")
    print("   • Email addresses")
    print("   • Phone numbers")
    print()
    
    response = input("Continue? (yes/no): ").strip().lower()
    
    if response in ['yes', 'y']:
        update_employees()
    else:
        print("\n❌ Update cancelled.")
