"""
Automatic Fix Script for app.py Duplicate Endpoints
Run this script to remove duplicate endpoints automatically
"""

import os
import shutil
from datetime import datetime

def fix_app_py():
    """Remove duplicate endpoints from app.py"""
    
    # Backup original file
    backup_name = f"app_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.py"
    print(f"📋 Creating backup: {backup_name}")
    shutil.copy('app.py', backup_name)
    
    # Read the file
    print("📖 Reading app.py...")
    with open('app.py', 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    print(f"📊 Total lines: {len(lines)}")
    
    # Find the duplicate section
    start_line = -1
    end_line = -1
    
    # Look for the start marker - the test-email route
    for i, line in enumerate(lines):
        if "@app.route('/test-email')" in line:
            start_line = i
            print(f"✅ Found start marker at line {i + 1}")
            break
    
    if start_line == -1:
        print("❌ Could not find start marker (@app.route('/test-email'))")
        print("⚠️  Your file might already be fixed!")
        return False
    
    # Look for the end marker - the leave-requests route after the old change_password
    for i in range(start_line, len(lines)):
        if '@app.route("/leave-requests"' in lines[i]:
            # This is our endpoint - go back a few lines to find where to stop deleting
            end_line = i - 1
            # Go back to skip empty lines
            while end_line > start_line and lines[end_line].strip() == '':
                end_line -= 1
            end_line += 1  # Include the last content line
            print(f"✅ Found end marker at line {end_line + 1}")
            break
    
    if end_line == -1:
        print("❌ Could not find end marker (@app.route('/leave-requests'))")
        print("⚠️  Manual deletion required")
        return False
    
    lines_to_delete = end_line - start_line + 1
    print(f"🗑️  Will delete {lines_to_delete} lines (from {start_line + 1} to {end_line + 1})")
    
    # Create new content without the duplicate section
    new_lines = lines[:start_line] + ['\n'] + lines[end_line + 1:]
    
    # Write the fixed content
    print("💾 Writing fixed version...")
    with open('app.py', 'w', encoding='utf-8') as f:
        f.writelines(new_lines)
    
    print("✅ Fix complete!")
    print(f"📁 Original file backed up to: {backup_name}")
    print(f"📊 Removed {lines_to_delete} lines")
    print(f"📊 New file has {len(new_lines)} lines (was {len(lines)})")
    
    return True

if __name__ == '__main__':
    print("=" * 60)
    print("HRMS app.py Automatic Fix Script")
    print("=" * 60)
    print()
    
    # Check if app.py exists
    if not os.path.exists('app.py'):
        print("❌ Error: app.py not found in current directory")
        print("📁 Please run this script from your project root directory")
        exit(1)
    
    # Confirm with user
    print("This script will:")
    print("  1. Create a backup of your current app.py")
    print("  2. Remove duplicate endpoint definitions")
    print("  3. Keep the new working implementations")
    print()
    
    response = input("Continue? (y/n): ").strip().lower()
    
    if response != 'y':
        print("❌ Operation cancelled")
        exit(0)
    
    print()
    
    # Run the fix
    success = fix_app_py()
    
    if success:
        print()
        print("=" * 60)
        print("🎉 SUCCESS! Your app.py has been fixed")
        print("=" * 60)
        print()
        print("Next steps:")
        print("  1. Run: python app.py")
        print("  2. Check that there are no errors")
        print("  3. Test the endpoints")
        print()
        print("If something went wrong, restore from backup:")
        print(f"  - Your backup is saved as: app_backup_*.py")
        print("  - Just rename it back to app.py")
    else:
        print()
        print("=" * 60)
        print("⚠️  Could not automatically fix")
        print("=" * 60)
        print()
        print("Please delete manually:")
        print("  1. Open app.py")
        print("  2. Find line with: @app.route('/test-email')")
        print("  3. Delete from there down to (but NOT including):")
        print("     @app.route('/leave-requests'")
