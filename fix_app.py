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
        content = f.read()
    
    # Find the section to delete
    # Start marker: first old notification endpoint
    start_marker = """@app.route('/test-email')
def test_email():
    msg = Message(
        subject="HRMS Email Test",
        recipients=["test@gmail.com"],
        body="HRMS email module is working correctly."
    )
    mail.send(msg)
    return {"message": "Email sent successfully"}, 200

@app.route('/api/notifications', methods=['GET'])
@jwt_required()
def get_notifications():
    """Get all notifications for the current user"""
    try:
        current_user = get_jwt_identity()
        user = User.query.filter_by(username=current_user).first()
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # For now, return sample notifications
        notifications_list = ["""
    
    # End marker: end of old change_password function (before leave-requests)
    end_marker = """        return jsonify({'error': str(e)}), 500
    


@app.route("/leave-requests", methods=["GET"])"""
    
    print("🔍 Searching for duplicate section...")
    
    # Find the positions
    start_pos = content.find(start_marker)
    end_pos = content.find(end_marker)
    
    if start_pos == -1:
        print("❌ Could not find start marker")
        print("⚠️  Your file might already be fixed or has different structure")
        return False
    
    if end_pos == -1:
        print("❌ Could not find end marker")
        print("⚠️  Your file might already be fixed or has different structure")
        return False
    
    print(f"✅ Found duplicate section at positions {start_pos} to {end_pos}")
    
    # Remove the duplicate section
    # Keep the leave-requests route marker
    new_content = content[:start_pos] + "\n" + content[end_pos + len("        return jsonify({'error': str(e)}), 500"):]
    
    # Write the fixed content
    print("💾 Writing fixed version...")
    with open('app.py', 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print("✅ Fix complete!")
    print(f"📁 Original file backed up to: {backup_name}")
    print(f"📊 Removed {len(content) - len(new_content)} characters")
    
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
        print("  - Find the backup file (app_backup_*.py)")
        print("  - Rename it back to app.py")
    else:
        print()
        print("=" * 60)
        print("⚠️  Could not automatically fix")
        print("=" * 60)
        print()
        print("Please use the manual deletion guide instead:")
        print("  - Open EXACT_DELETION_GUIDE.md")
        print("  - Follow the step-by-step instructions")
