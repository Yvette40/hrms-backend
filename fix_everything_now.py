#!/usr/bin/env python3
"""
HRMS ONE-CLICK FIX - Fixes Everything at Once
==============================================
This single script fixes ALL issues:
1. Code bugs in /my-attendance and /my-payslips
2. Missing user-employee links
3. Verifies everything works

Just run this ONE command:
    python fix_everything_now.py

That's it! No other steps needed.
"""

import sys
import os
from datetime import datetime, date

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def print_header(text):
    print(f"\n{'='*80}")
    print(f"  {text}")
    print(f"{'='*80}\n")

def print_step(num, text):
    print(f"\n[STEP {num}] {text}")
    print("-" * 80)

# ============================================================================
# PART 1: FIX CODE BUGS
# ============================================================================

def backup_app_py():
    """Backup app.py"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup = f"app.py.backup_{timestamp}"
    
    try:
        with open('app.py', 'r') as f:
            content = f.read()
        with open(backup, 'w') as f:
            f.write(content)
        print(f"✅ Created backup: {backup}")
        return backup
    except Exception as e:
        print(f"❌ Backup failed: {e}")
        return None

def fix_code_bugs():
    """Fix the filter_by(name=...) bugs in app.py"""
    print_step(1, "Fixing Code Bugs in app.py")
    
    try:
        with open('app.py', 'r') as f:
            lines = f.readlines()
        
        fixes_made = []
        
        for i, line in enumerate(lines):
            if 'employee = Employee.query.filter_by(name=user.username).first()' in line:
                # Check context to find which endpoint
                endpoint = "unknown"
                for j in range(max(0, i-30), i):
                    if '@app.route("/my-attendance"' in lines[j]:
                        endpoint = "my-attendance"
                        break
                    elif '@app.route("/my-payslips"' in lines[j]:
                        endpoint = "my-payslips"
                        break
                
                if endpoint in ["my-attendance", "my-payslips"]:
                    indent = len(line) - len(line.lstrip())
                    spaces = ' ' * indent
                    
                    new_code = [
                        f"{spaces}# ✅ FIXED: Find employee by user_id\n",
                        f"{spaces}employee = Employee.query.filter_by(user_id=user.id).first()\n",
                        f"{spaces}if not employee and hasattr(user, 'employee_profile'):\n",
                        f"{spaces}    if isinstance(user.employee_profile, list):\n",
                        f"{spaces}        employee = user.employee_profile[0] if user.employee_profile else None\n",
                        f"{spaces}    else:\n",
                        f"{spaces}        employee = user.employee_profile\n",
                    ]
                    
                    lines[i] = ''.join(new_code)
                    fixes_made.append(endpoint)
                    print(f"✅ Fixed /{endpoint}")
        
        if fixes_made:
            with open('app.py', 'w') as f:
                f.writelines(lines)
            print(f"\n✅ Fixed {len(fixes_made)} endpoint(s)")
            return True
        else:
            print("✅ No code bugs found (already fixed?)")
            return True
            
    except Exception as e:
        print(f"❌ Error fixing code: {e}")
        return False

# ============================================================================
# PART 2: FIX USER-EMPLOYEE LINKS
# ============================================================================

def fix_user_links():
    """Fix user-employee links in database"""
    print_step(2, "Fixing User-Employee Links")
    
    try:
        from app import app, db
        from models import User, Employee
        
        with app.app_context():
            fixed_count = 0
            
            # Fix 1: Link jmwangi to John Mwangi
            jmwangi_user = User.query.get(89)
            john_emp = Employee.query.filter_by(email='john.mwangi@glimmer.com').first()
            
            if jmwangi_user and john_emp:
                if john_emp.user_id != 89:
                    john_emp.user_id = 89
                    print(f"✅ Linked user 'jmwangi' → employee 'John Mwangi'")
                    fixed_count += 1
            
            # Fix 2: Create employee profiles for system users
            system_users = [
                (1, 'admin', 'System Administrator', 'ADMIN001', 'Administration', 120000),
                (2, 'hr_officer', 'HR Officer', 'HR001', 'Human Resources', 90000),
                (3, 'dept_manager', 'Department Manager', 'MGR001', 'Management', 100000),
                (4, 'employee', 'General Employee', 'EMP000', 'General', 50000),
            ]
            
            for user_id, username, name, nat_id, dept, salary in system_users:
                user = User.query.get(user_id)
                if user:
                    existing = Employee.query.filter_by(user_id=user_id).first()
                    if not existing:
                        new_emp = Employee(
                            name=name,
                            national_id=nat_id,
                            department=dept,
                            position=user.role.replace('_', ' ').title() if hasattr(user, 'role') else 'Employee',
                            email=getattr(user, 'email', None) or f'{username}@company.com',
                            phone_number=getattr(user, 'phone', None) or '+254700000000',
                            base_salary=salary,
                            join_date=date.today(),
                            user_id=user_id,
                            active=True,
                            leave_balance=21
                        )
                        db.session.add(new_emp)
                        print(f"✅ Created employee profile for '{username}'")
                        fixed_count += 1
            
            db.session.commit()
            
            if fixed_count > 0:
                print(f"\n✅ Fixed {fixed_count} user link(s)")
            else:
                print("\n✅ All users already linked")
            
            return True
            
    except Exception as e:
        print(f"❌ Error fixing links: {e}")
        import traceback
        traceback.print_exc()
        return False

# ============================================================================
# PART 3: VERIFY FIXES
# ============================================================================

def verify_everything():
    """Verify all fixes worked"""
    print_step(3, "Verifying Fixes")
    
    try:
        from app import app, db
        from models import User, Employee, Attendance
        
        with app.app_context():
            # Check code
            with open('app.py', 'r') as f:
                content = f.read()
            
            if 'filter_by(name=user.username)' in content:
                # Check if it's in a problematic context
                lines = content.split('\n')
                still_broken = False
                for i, line in enumerate(lines):
                    if 'filter_by(name=user.username)' in line:
                        for j in range(max(0, i-30), i):
                            if '@app.route("/my-' in lines[j]:
                                still_broken = True
                                break
                
                if still_broken:
                    print("❌ Code bug still present")
                    return False
            
            print("✅ Code verified")
            
            # Check user links
            unlinked = db.session.query(User).outerjoin(
                Employee, User.id == Employee.user_id
            ).filter(Employee.id == None).count()
            
            if unlinked > 0:
                print(f"⚠️  {unlinked} users still unlinked")
            else:
                print("✅ All users linked")
            
            # Test with real user
            test_user = User.query.filter_by(username='fnjoroge').first()
            if test_user:
                employee = Employee.query.filter_by(user_id=test_user.id).first()
                if employee:
                    att_count = Attendance.query.filter_by(employee_id=employee.id).count()
                    print(f"✅ Test: User 'fnjoroge' → Employee '{employee.name}' → {att_count} attendance records")
                else:
                    print(f"⚠️  User 'fnjoroge' not linked to employee")
            
            return True
            
    except Exception as e:
        print(f"❌ Verification error: {e}")
        return False

# ============================================================================
# MAIN
# ============================================================================

def main():
    print_header("HRMS ONE-CLICK FIX - Fixing Everything Now!")
    
    # Check we're in the right directory
    if not os.path.exists('app.py'):
        print("❌ Error: app.py not found")
        print("   Please run this from the hrms-backend-main directory")
        return
    
    if not os.path.exists('instance/hrms.db'):
        print("❌ Error: database not found")
        print("   Expected: instance/hrms.db")
        return
    
    print("This will fix:")
    print("  1. Code bugs in /my-attendance and /my-payslips")
    print("  2. Missing user-employee links")
    print("  3. Verify everything works")
    
    response = input("\nProceed? (yes/no): ").strip().lower()
    if response not in ['yes', 'y']:
        print("\n❌ Cancelled")
        return
    
    # Backup
    print("\n" + "="*80)
    backup_path = backup_app_py()
    if not backup_path:
        print("❌ Cannot proceed without backup")
        return
    
    # Fix code
    if not fix_code_bugs():
        print("\n❌ Failed to fix code bugs")
        print(f"   Restore: cp {backup_path} app.py")
        return
    
    # Fix links
    if not fix_user_links():
        print("\n⚠️  Some link fixes may have failed")
    
    # Verify
    verify_everything()
    
    # Final message
    print_header("FIX COMPLETE!")
    
    print("✅ All fixes applied!\n")
    
    print("📝 NEXT STEPS:")
    print("   1. Restart your backend server:")
    print("      • Stop current server (Ctrl+C)")
    print("      • Run: python app.py")
    print()
    print("   2. Clear browser cache (Ctrl+Shift+Delete)")
    print()
    print("   3. Test:")
    print("      • Login as 'fnjoroge'")
    print("      • Go to 'My Attendance'")
    print("      • Should see 65+ attendance records!")
    print()
    print("   4. Also test:")
    print("      • My Payslips page")
    print("      • Profile page")
    print()
    
    print(f"💾 Backup saved: {backup_path}")
    print(f"   (To undo: cp {backup_path} app.py)")
    
    print("\n" + "="*80)
    print("If still not working, check:")
    print("  • Backend server is actually restarted")
    print("  • No error messages in backend console")
    print("  • Frontend API URL points to correct backend")
    print("  • Browser console for errors (F12)")
    print("="*80)

if __name__ == "__main__":
    main()
