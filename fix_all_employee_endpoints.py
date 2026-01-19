#!/usr/bin/env python3
"""
HRMS Complete Employee Endpoints Fix
=====================================
This script fixes ALL broken employee endpoints in app.py

Endpoints Fixed:
1. /my-attendance (line ~2612) - ❌ Uses filter_by(name=...)
2. /my-payslips (line ~2574)   - ❌ Uses filter_by(name=...)
3. /my-leaves (line ~2707)     - ✅ Already correct!

The Bug:
    employee = Employee.query.filter_by(name=user.username).first()
    
    This tries to match employee records by name, but usernames often
    don't match employee names exactly:
    - User: "jmwangi" vs Employee: "John Mwangi" → NO MATCH
    - User: "fnjoroge" vs Employee: "Francis Njoroge" → NO MATCH

The Fix:
    employee = Employee.query.filter_by(user_id=user.id).first()
    
    This uses the proper foreign key relationship to find the employee.

Usage:
    python fix_all_employee_endpoints.py
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

def find_broken_endpoints(filepath):
    """Find all endpoints with the broken pattern"""
    try:
        with open(filepath, 'r') as f:
            lines = f.readlines()
        
        broken_endpoints = []
        
        for i, line in enumerate(lines):
            if 'employee = Employee.query.filter_by(name=user.username).first()' in line:
                # Find which endpoint this belongs to
                endpoint_name = None
                for j in range(max(0, i-30), i):
                    if '@app.route' in lines[j]:
                        # Extract route name
                        route_line = lines[j]
                        if '"/my-' in route_line or '"/employee' in route_line:
                            endpoint_name = route_line.split('"')[1]
                            break
                
                broken_endpoints.append({
                    'line_num': i + 1,
                    'endpoint': endpoint_name or 'Unknown',
                    'line_index': i
                })
        
        return broken_endpoints
    except Exception as e:
        print(f"Error scanning file: {str(e)}")
        return []

def fix_endpoint(lines, line_index):
    """Fix a single endpoint by replacing the broken line"""
    
    line = lines[line_index]
    indent = len(line) - len(line.lstrip())
    spaces = ' ' * indent
    
    # Generate the correct code with same indentation
    new_code = [
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
    
    # Replace the single line with the new multi-line code
    lines[line_index] = ''.join(new_code)
    
    return lines

def fix_all_endpoints(filepath):
    """Fix all broken endpoints in the file"""
    
    try:
        # Find broken endpoints
        broken = find_broken_endpoints(filepath)
        
        if not broken:
            print("✅ No broken endpoints found! File may already be fixed.")
            return False, []
        
        print(f"\n📋 Found {len(broken)} broken endpoint(s):")
        for item in broken:
            print(f"   • {item['endpoint']} (line {item['line_num']})")
        
        # Read file
        with open(filepath, 'r') as f:
            lines = f.readlines()
        
        # Fix each endpoint (go in reverse to preserve line numbers)
        fixed_endpoints = []
        for item in reversed(broken):
            lines = fix_endpoint(lines, item['line_index'])
            fixed_endpoints.append(item['endpoint'])
            print(f"   ✅ Fixed: {item['endpoint']}")
        
        # Write back to file
        with open(filepath, 'w') as f:
            f.writelines(lines)
        
        return True, list(reversed(fixed_endpoints))
        
    except Exception as e:
        print(f"❌ Error fixing endpoints: {str(e)}")
        return False, []

def verify_fixes(filepath):
    """Verify that all fixes were applied correctly"""
    try:
        with open(filepath, 'r') as f:
            content = f.read()
            lines = content.split('\n')
        
        # Check that the broken pattern is gone
        remaining_broken = []
        for i, line in enumerate(lines):
            if 'filter_by(name=user.username)' in line:
                # Check if it's in an employee endpoint context
                for j in range(max(0, i-30), i):
                    if '@app.route("/my-' in lines[j] or '@app.route("/employee' in lines[j]:
                        remaining_broken.append(i + 1)
                        break
        
        # Check that the new pattern exists
        has_new_pattern = 'filter_by(user_id=user.id)' in content
        
        if not remaining_broken and has_new_pattern:
            print("✅ Verification passed: All endpoints fixed correctly!")
            return True
        else:
            if remaining_broken:
                print(f"⚠️  Warning: Still found broken pattern at lines: {remaining_broken}")
            if not has_new_pattern:
                print(f"⚠️  Warning: New pattern not found in file")
            return False
            
    except Exception as e:
        print(f"❌ Error verifying fixes: {str(e)}")
        return False

def show_summary(fixed_endpoints):
    """Show a summary of what was fixed"""
    print("\n" + "="*80)
    print("  SUMMARY OF CHANGES")
    print("="*80 + "\n")
    
    print("Fixed Endpoints:")
    for endpoint in fixed_endpoints:
        print(f"  ✅ {endpoint}")
    
    print("\n" + "─"*80)
    print("BEFORE (Broken):")
    print("─"*80)
    print("employee = Employee.query.filter_by(name=user.username).first()")
    print()
    print("❌ Problem: Matches by NAME, which often doesn't match username")
    print("   Example: user 'jmwangi' vs employee 'John Mwangi' → NO MATCH")
    
    print("\n" + "─"*80)
    print("AFTER (Fixed):")
    print("─"*80)
    print("# ✅ FIXED: Find employee by user_id relationship")
    print("employee = Employee.query.filter_by(user_id=user.id).first()")
    print()
    print("# Fallback: Try using the relationship attribute")
    print("if not employee and hasattr(user, 'employee_profile'):")
    print("    employee = user.employee_profile")
    print()
    print("✅ Solution: Uses proper foreign key relationship")

def main():
    """Main execution function"""
    print_header("HRMS Complete Employee Endpoints Fix")
    
    # Check if app.py exists
    app_file = 'app.py'
    if not os.path.exists(app_file):
        print(f"❌ Error: {app_file} not found in current directory")
        print(f"   Current directory: {os.getcwd()}")
        print(f"\n   Please run this script from the hrms-backend-main directory:")
        print(f"   cd /path/to/hrms-backend-main")
        print(f"   python fix_all_employee_endpoints.py")
        return
    
    print(f"Found: {app_file}")
    print(f"Location: {os.path.abspath(app_file)}\n")
    
    # Scan for issues
    print("Scanning for broken endpoints...")
    broken = find_broken_endpoints(app_file)
    
    if not broken:
        print("✅ No broken endpoints found!")
        print("   All employee endpoints appear to be using the correct pattern.")
        print("\n   Note: Make sure you still run fix_employee_profiles.py to link")
        print("         users to their employee records.")
        return
    
    print(f"\n⚠️  Found {len(broken)} endpoint(s) with the broken pattern:\n")
    for item in broken:
        print(f"   • {item['endpoint']} at line {item['line_num']}")
    
    print("\nThis script will:")
    print("  • Create a backup of app.py")
    print("  • Fix all broken employee lookup patterns")
    print("  • Change: filter_by(name=...) → filter_by(user_id=...)")
    print("  • Verify the fixes")
    
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
    
    # Step 2: Apply fixes
    print("\nApplying fixes...")
    success, fixed_endpoints = fix_all_endpoints(app_file)
    
    if not success:
        if not fixed_endpoints:
            print("\n⚠️  No fixes applied. File may already be correct.")
        else:
            print("\n❌ Fix process failed.")
        print(f"   Original file backed up at: {backup_path}")
        return
    
    # Step 3: Verify fixes
    print("\nVerifying fixes...")
    if not verify_fixes(app_file):
        print("\n⚠️  Verification had warnings. Please review the changes.")
        print(f"   Original file backed up at: {backup_path}")
    
    # Step 4: Show summary
    show_summary(fixed_endpoints)
    
    # Success message
    print_header("FIX COMPLETE")
    print(f"✅ Successfully fixed {len(fixed_endpoints)} endpoint(s)!\n")
    print(f"📋 Summary:")
    print(f"   • Backup: {backup_path}")
    print(f"   • Fixed: {', '.join(fixed_endpoints)}")
    
    print(f"\n📝 Next Steps:")
    print(f"   1. Restart your Flask backend server")
    print(f"   2. Run: python fix_employee_profiles.py")
    print(f"      (This links users to their employee records)")
    print(f"   3. Test the fixed endpoints:")
    print(f"      • Login as employee and check 'My Attendance'")
    print(f"      • Check 'My Payslips'")
    print(f"      • Verify all data displays correctly")
    
    print(f"\n🔄 To undo (if needed):")
    print(f"   cp {backup_path} {app_file}")
    
    print("\n💡 Tip: After fixing, test with user 'fnjoroge' who has:")
    print("   • 65 attendance records")
    print("   • Should now display correctly!")

if __name__ == "__main__":
    main()
