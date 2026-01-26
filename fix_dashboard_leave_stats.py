"""
QUICK FIX: Dashboard Leave Statistics
This script fixes the hardcoded TODO for leave request counts in the dashboard
Run this after backing up app.py
"""

import os
import sys

def fix_dashboard_stats():
    """Fix the leave request statistics in dashboard endpoint"""
    
    app_file = "hrms-backend-main/app.py"
    
    if not os.path.exists(app_file):
        print(f"❌ Error: {app_file} not found!")
        print("Make sure you run this script from the parent directory of hrms-backend-main")
        return False
    
    # Create backup
    backup_file = f"{app_file}.backup_{os.urandom(4).hex()}"
    os.system(f"cp {app_file} {backup_file}")
    print(f"✅ Created backup: {backup_file}")
    
    # Read the file
    with open(app_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # The lines to find and replace
    old_code = """        leave_requests = 0  # TODO: Implement when LeaveRequest model exists
        on_leave = 0  # TODO: Implement when LeaveRequest model exists"""
    
    new_code = """        # Get actual leave request counts
        from datetime import date
        leave_requests = LeaveRequest.query.filter_by(status='Pending').count()
        today = date.today()
        on_leave = LeaveRequest.query.filter(
            and_(
                LeaveRequest.status == 'Approved',
                LeaveRequest.start_date <= today,
                LeaveRequest.end_date >= today
            )
        ).count()"""
    
    # Replace
    if old_code in content:
        content = content.replace(old_code, new_code)
        
        # Write back
        with open(app_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("✅ Fixed dashboard leave statistics!")
        print("\nChanges made:")
        print("- Replaced hardcoded leave_requests = 0")
        print("- Replaced hardcoded on_leave = 0")
        print("- Added actual database queries for both values")
        return True
    else:
        print("⚠️  Could not find the exact code to replace.")
        print("The TODO might have already been fixed or the code format changed.")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("HRMS Dashboard Leave Statistics Fix")
    print("=" * 60)
    
    success = fix_dashboard_stats()
    
    if success:
        print("\n✅ Fix applied successfully!")
        print("\nNext steps:")
        print("1. Review the changes in hrms-backend-main/app.py")
        print("2. Restart your Flask server")
        print("3. Test the dashboard to verify leave counts show correctly")
    else:
        print("\n❌ Fix failed. Please apply changes manually.")
