#!/usr/bin/env python3
"""
HRMS Attendance Endpoint Fix Script
====================================
This script automatically fixes the broken /my-attendance endpoint in app.py

The bug: Line 2612 uses filter_by(name=user.username) instead of filter_by(user_id=user.id)
This causes attendance data to not display for employees.

Usage:
    python fix_attendance_endpoint.py
"""

import sys
import os
from datetime import datetime

def print_header(text):
    """Print a formatted header"""
    print(f"\n{'='*80}")
    print(f"  {text}")
    print(f"{'='*80}\n")

def backup_file(filepath):
    """Create a backup of the original file"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_path = f"{filepath}.backup_{timestamp}"
    
    try:
        with open(filepath, 'r') as f:
            content = f.read()
        
        with open(backup_path, 'w') as f:
            f.write(content)
        
        print(f"✅ Backup created: {backup_path}")
        return backup_path
    except Exception as e:
        print(f"❌ Error creating backup: {str(e)}")
        return None

def check_if_already_fixed(filepath):
    """Check if the file has already been fixed"""
    try:
        with open(filepath, 'r') as f:
            content = f.read()
        
        # Look for the correct code pattern
        if 'Employee.query.filter_by(user_id=user.id)' in content:
            # Check if it's in the my-attendance endpoint
            lines = content.split('\n')
            in_my_attendance = False
            for i, line in enumerate(lines):
                if '@app.route("/my-attendance"' in line:
                    in_my_attendance = True
                elif in_my_attendance and 'Employee.query.filter_by(user_id=user.id)' in line:
                    return True
                elif in_my_attendance and '@app.route' in line and i > 0:
                    break
        
        return False
    except Exception as e:
        print(f"Error checking file: {str(e)}")
        return False

def fix_attendance_endpoint(filepath):
    """Fix the my-attendance endpoint in app.py"""
    
    try:
        with open(filepath, 'r') as f:
            lines = f.readlines()
        
        # Find and fix the problematic line
        fixed = False
        fix_line_number = None
        
        for i, line in enumerate(lines):
            # Look for the broken line
            if 'employee = Employee.query.filter_by(name=user.username).first()' in line:
                # Check if this is in the my-attendance function
                # Look backwards to confirm we're in the right function
                in_my_attendance = False
                for j in range(max(0, i-20), i):
                    if '@app.route("/my-attendance"' in lines[j] or 'def get_my_attendance' in lines[j]:
                        in_my_attendance = True
                        break
                
                if in_my_attendance:
                    # Get the indentation
                    indent = len(line) - len(line.lstrip())
                    spaces = ' ' * indent
                    
                    # Replace with the correct code
                    new_lines = [
                        f"{spaces}# ✅ FIXED: Find employee by user_id relationship\n",
                        f"{spaces}employee = None\n",
                        f"{spaces}\n",
                        f"{spaces}# Try getting employee via user_id foreign key\n",
                        f"{spaces}employee = Employee.query.filter_by(user_id=user.id).first()\n",
                        f"{spaces}\n",
                        f"{spaces}# Fallback: Try using the relationship attribute\n",
                        f"{spaces}if not employee and hasattr(user, 'employee_profile'):\n",
                        f"{spaces}    if isinstance(user.employee_profile, list):\n",
                        f"{spaces}        employee = user.employee_profile[0] if user.employee_profile else None\n",
                        f"{spaces}    else:\n",
                        f"{spaces}        employee = user.employee_profile\n",
                    ]
                    
                    # Replace the single broken line with the new code
                    lines[i] = ''.join(new_lines)
                    fixed = True
                    fix_line_number = i + 1
                    
                    print(f"✅ Fixed line {fix_line_number}: Changed filter_by(name=...) to filter_by(user_id=...)")
                    break
        
        if not fixed:
            print("⚠️  Could not find the expected broken code pattern.")
            print("    The file may have been modified or already fixed.")
            return False
        
        # Write the fixed content back
        with open(filepath, 'w') as f:
            f.writelines(lines)
        
        print(f"✅ File updated successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error fixing file: {str(e)}")
        return False

def verify_fix(filepath):
    """Verify that the fix was applied correctly"""
    try:
        with open(filepath, 'r') as f:
            content = f.read()
        
        # Check for the new code
        if 'employee = Employee.query.filter_by(user_id=user.id).first()' in content:
            # Make sure the old broken code is gone from my-attendance
            lines = content.split('\n')
            in_my_attendance = False
            has_old_code = False
            has_new_code = False
            
            for i, line in enumerate(lines):
                if '@app.route("/my-attendance"' in line:
                    in_my_attendance = True
                elif in_my_attendance and '@app.route' in line and i > 0:
                    break
                elif in_my_attendance:
                    if 'filter_by(name=user.username)' in line:
                        has_old_code = True
                    if 'filter_by(user_id=user.id)' in line:
                        has_new_code = True
            
            if has_new_code and not has_old_code:
                print("✅ Verification passed: Fix applied correctly!")
                return True
            else:
                print("⚠️  Verification failed: Code may not be correct")
                return False
        else:
            print("⚠️  Verification failed: Expected code not found")
            return False
            
    except Exception as e:
        print(f"❌ Error verifying fix: {str(e)}")
        return False

def show_diff(filepath, backup_path):
    """Show what was changed"""
    try:
        print("\n" + "="*80)
        print("  CHANGES MADE")
        print("="*80 + "\n")
        
        print("BEFORE (Broken):")
        print("─" * 80)
        print("employee = Employee.query.filter_by(name=user.username).first()")
        print("─" * 80)
        
        print("\nAFTER (Fixed):")
        print("─" * 80)
        print("# ✅ FIXED: Find employee by user_id relationship")
        print("employee = None")
        print("")
        print("# Try getting employee via user_id foreign key")
        print("employee = Employee.query.filter_by(user_id=user.id).first()")
        print("")
        print("# Fallback: Try using the relationship attribute")
        print("if not employee and hasattr(user, 'employee_profile'):")
        print("    if isinstance(user.employee_profile, list):")
        print("        employee = user.employee_profile[0] if user.employee_profile else None")
        print("    else:")
        print("        employee = user.employee_profile")
        print("─" * 80)
        
    except Exception as e:
        print(f"Error showing diff: {str(e)}")

def main():
    """Main execution function"""
    print_header("HRMS Attendance Endpoint Fix Script")
    
    # Check if app.py exists
    app_file = 'app.py'
    if not os.path.exists(app_file):
        print(f"❌ Error: {app_file} not found in current directory")
        print(f"   Current directory: {os.getcwd()}")
        print(f"\n   Please run this script from the hrms-backend-main directory:")
        print(f"   cd /path/to/hrms-backend-main")
        print(f"   python fix_attendance_endpoint.py")
        return
    
    print(f"Found: {app_file}")
    print(f"Location: {os.path.abspath(app_file)}\n")
    
    # Check if already fixed
    if check_if_already_fixed(app_file):
        print("✅ The attendance endpoint appears to already be fixed!")
        print("   No changes needed.")
        response = input("\n   Do you want to proceed anyway? (yes/no): ").strip().lower()
        if response not in ['yes', 'y']:
            print("\n   Operation cancelled.")
            return
    
    print("This script will fix the /my-attendance endpoint bug:")
    print("  • Changes: filter_by(name=...) → filter_by(user_id=...)")
    print("  • Effect: Employees will be able to see their attendance data")
    print("  • Safety: Creates backup before making changes")
    
    response = input("\nDo you want to proceed? (yes/no): ").strip().lower()
    if response not in ['yes', 'y']:
        print("\n❌ Operation cancelled by user")
        return
    
    print("\n" + "─"*80)
    print("Starting fix process...")
    print("─"*80)
    
    # Step 1: Create backup
    backup_path = backup_file(app_file)
    if not backup_path:
        print("\n❌ Cannot proceed without backup. Aborting.")
        return
    
    # Step 2: Apply fix
    print("\nApplying fix...")
    if not fix_attendance_endpoint(app_file):
        print("\n❌ Fix failed. Your original file is backed up at:")
        print(f"   {backup_path}")
        return
    
    # Step 3: Verify fix
    print("\nVerifying fix...")
    if not verify_fix(app_file):
        print("\n⚠️  Verification failed. Please check the file manually.")
        print(f"   Original file backed up at: {backup_path}")
        return
    
    # Step 4: Show diff
    show_diff(app_file, backup_path)
    
    # Success message
    print_header("FIX COMPLETE")
    print("✅ The attendance endpoint has been fixed successfully!")
    print(f"\n📋 Summary:")
    print(f"   • Original file backed up to: {backup_path}")
    print(f"   • Fixed file: {app_file}")
    print(f"   • Changed: Employee lookup from name to user_id")
    
    print(f"\n📝 Next Steps:")
    print(f"   1. Restart your Flask backend server")
    print(f"   2. Run: python fix_employee_profiles.py (if not done already)")
    print(f"   3. Login as an employee and check 'My Attendance' page")
    print(f"   4. Verify attendance data now displays correctly")
    
    print(f"\n🔄 To undo this fix (if needed):")
    print(f"   cp {backup_path} {app_file}")

if __name__ == "__main__":
    main()
