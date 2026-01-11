"""
COMPLETE FIX: Update Employees + Create User Accounts
This script fixes BOTH issues:
1. Updates employee data (department, position, email, phone)
2. Creates user accounts for each employee
3. Links employees to their user accounts

Usage: python complete_fix_employees.py
"""

try:
    from app import app, db
    from models import User, Employee
    from werkzeug.security import generate_password_hash
except ImportError:
    print("❌ Error: Cannot import app modules.")
    print("Make sure this script is in your project directory with app.py and models.py")
    import sys
    sys.exit(1)

# Complete employee data with user credentials
EMPLOYEE_DATA = {
    '12345678': {
        'name': 'John Mwangi',
        'department': 'Engineering',
        'position': 'Software Engineer',
        'email': 'john.mwangi@glimmer.com',
        'phone_number': '+254712345678',
        'username': 'jmwangi',
        'password': 'password123'
    },
    '23456789': {
        'name': 'Mary Wanjiku',
        'department': 'Finance',
        'position': 'Accountant',
        'email': 'mary.wanjiku@glimmer.com',
        'phone_number': '+254723456789',
        'username': 'mwanjiku',
        'password': 'password123'
    },
    '34567890': {
        'name': 'Peter Omondi',
        'department': 'Sales',
        'position': 'Sales Manager',
        'email': 'peter.omondi@glimmer.com',
        'phone_number': '+254734567890',
        'username': 'pomondi',
        'password': 'password123'
    },
    '45678901': {
        'name': 'Jane Akinyi',
        'department': 'Marketing',
        'position': 'Marketing Officer',
        'email': 'jane.akinyi@glimmer.com',
        'phone_number': '+254745678901',
        'username': 'jakinyi',
        'password': 'password123'
    },
    '56789012': {
        'name': 'David Kamau',
        'department': 'Engineering',
        'position': 'Senior Developer',
        'email': 'david.kamau@glimmer.com',
        'phone_number': '+254756789012',
        'username': 'dkamau',
        'password': 'password123'
    },
    '67890123': {
        'name': 'Grace Njeri',
        'department': 'HR',
        'position': 'HR Assistant',
        'email': 'grace.njeri@glimmer.com',
        'phone_number': '+254767890123',
        'username': 'gnjeri',
        'password': 'password123'
    },
    '78901234': {
        'name': 'James Otieno',
        'department': 'Operations',
        'position': 'Operations Manager',
        'email': 'james.otieno@glimmer.com',
        'phone_number': '+254778901234',
        'username': 'jotieno',
        'password': 'password123'
    },
    '89012345': {
        'name': 'Lucy Chebet',
        'department': 'Finance',
        'position': 'Financial Analyst',
        'email': 'lucy.chebet@glimmer.com',
        'phone_number': '+254789012345',
        'username': 'lchebet',
        'password': 'password123'
    },
    '90123456': {
        'name': 'Samuel Kipchoge',
        'department': 'Sales',
        'position': 'Sales Executive',
        'email': 'samuel.kipchoge@glimmer.com',
        'phone_number': '+254790123456',
        'username': 'skipchoge',
        'password': 'password123'
    },
    '01234567': {
        'name': 'Rose Wambui',
        'department': 'Admin',
        'position': 'Office Administrator',
        'email': 'rose.wambui@glimmer.com',
        'phone_number': '+254701234567',
        'username': 'rwambui',
        'password': 'password123'
    },
    '11234568': {
        'name': 'Patrick Mutua',
        'department': 'IT',
        'position': 'IT Support Specialist',
        'email': 'patrick.mutua@glimmer.com',
        'phone_number': '+254711234568',
        'username': 'pmutua',
        'password': 'password123'
    },
    '21234569': {
        'name': 'Susan Nyambura',
        'department': 'Customer Service',
        'position': 'Customer Service Representative',
        'email': 'susan.nyambura@glimmer.com',
        'phone_number': '+254721234569',
        'username': 'snyambura',
        'password': 'password123'
    },
    '31234560': {
        'name': 'Michael Ochieng',
        'department': 'Logistics',
        'position': 'Logistics Coordinator',
        'email': 'michael.ochieng@glimmer.com',
        'phone_number': '+254731234560',
        'username': 'mochieng',
        'password': 'password123'
    },
    '41234561': {
        'name': 'Ann Muthoni',
        'department': 'Legal',
        'position': 'Legal Officer',
        'email': 'ann.muthoni@glimmer.com',
        'phone_number': '+254741234561',
        'username': 'amuthoni',
        'password': 'password123'
    },
    '51234562': {
        'name': 'Robert Kariuki',
        'department': 'Procurement',
        'position': 'Procurement Officer',
        'email': 'robert.kariuki@glimmer.com',
        'phone_number': '+254751234562',
        'username': 'rkariuki',
        'password': 'password123'
    }
}

def complete_fix():
    """Update employees and create user accounts"""
    
    print("\n" + "="*80)
    print("COMPLETE FIX: Updating Employees + Creating User Accounts")
    print("="*80 + "\n")
    
    with app.app_context():
        updated_count = 0
        user_created_count = 0
        user_linked_count = 0
        skipped_count = 0
        
        for national_id, data in EMPLOYEE_DATA.items():
            # Find the employee
            employee = Employee.query.filter_by(national_id=national_id).first()
            
            if not employee:
                print(f"⚠️  Employee with ID {national_id} not found - skipping")
                skipped_count += 1
                continue
            
            print(f"\n📋 Processing: {data['name']}")
            print("-" * 60)
            
            # Step 1: Update employee data
            employee.department = data['department']
            employee.position = data['position']
            employee.email = data['email']
            employee.phone_number = data['phone_number']
            print(f"   ✅ Updated employee data")
            print(f"      → Department: {data['department']}")
            print(f"      → Position: {data['position']}")
            updated_count += 1
            
            # Step 2: Create or find user account
            user = User.query.filter_by(username=data['username']).first()
            
            if not user:
                # Create new user account
                user = User(
                    username=data['username'],
                    role='Employee',
                    email=data['email'],
                    phone=data['phone_number']
                )
                user.set_password(data['password'])
                db.session.add(user)
                db.session.flush()  # Get the user ID
                print(f"   ✅ Created user account")
                print(f"      → Username: {data['username']}")
                print(f"      → Password: {data['password']}")
                user_created_count += 1
            else:
                print(f"   ⏭️  User account already exists: {data['username']}")
            
            # Step 3: Link employee to user
            if employee.user_id is None:
                employee.user_id = user.id
                print(f"   ✅ Linked employee to user account")
                user_linked_count += 1
            else:
                print(f"   ⏭️  Employee already linked to user")
        
        # Commit all changes
        db.session.commit()
        
        print("\n" + "="*80)
        print("✅ COMPLETE FIX FINISHED!")
        print("="*80 + "\n")
        
        print(f"📊 Summary:")
        print(f"   • Employees updated: {updated_count}")
        print(f"   • User accounts created: {user_created_count}")
        print(f"   • Employees linked to users: {user_linked_count}")
        if skipped_count > 0:
            print(f"   • Skipped: {skipped_count}")
        
        print("\n" + "-"*80)
        print("🔐 LOGIN CREDENTIALS:")
        print("-"*80)
        print(f"{'Username':<15} {'Password':<15} {'Name':<25} {'Department':<15}")
        print("-"*80)
        
        for national_id, data in list(EMPLOYEE_DATA.items())[:10]:
            print(f"{data['username']:<15} {data['password']:<15} {data['name']:<25} {data['department']:<15}")
        
        print("\n💡 All employees can now:")
        print("   ✅ Log in to the system")
        print("   ✅ Appear on employee pages")
        print("   ✅ Access employee features")
        print("   ✅ View their own data")
        
        # Verify the fix
        print("\n" + "="*80)
        print("🔍 VERIFICATION")
        print("="*80)
        
        employees_with_users = Employee.query.filter(Employee.user_id.isnot(None)).count()
        total_employees = Employee.query.count()
        
        print(f"   • Total employees: {total_employees}")
        print(f"   • Employees with user accounts: {employees_with_users}")
        print(f"   • Coverage: {(employees_with_users/total_employees*100):.1f}%")
        
        print("\n" + "="*80)
        print("✅ ALL DONE! Your employees should now appear on all pages!")
        print("="*80)

if __name__ == "__main__":
    print("\n⚠️  This script will:")
    print("   1. Update employee data (department, position, email, phone)")
    print("   2. Create user accounts for each employee")
    print("   3. Link employees to their user accounts")
    print("\n   All employees will use password: password123")
    print()
    
    response = input("Continue? (yes/no): ").strip().lower()
    
    if response in ['yes', 'y']:
        complete_fix()
    else:
        print("\n❌ Fix cancelled.")
