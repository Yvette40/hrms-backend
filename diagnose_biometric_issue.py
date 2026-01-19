#!/usr/bin/env python3
"""
DIAGNOSTIC SCRIPT - Find Why Biometric Data Not Showing
========================================================
This will check every step and tell you exactly what's wrong.

Usage:
    python diagnose_biometric_issue.py
"""

import os
import sys
import sqlite3

def check_database():
    """Check if database has the biometric data"""
    print("=" * 80)
    print("  STEP 1: Checking Database")
    print("=" * 80)
    print()
    
    db_path = 'instance/hrms.db'
    
    if not os.path.exists(db_path):
        print(f"❌ Database not found at: {db_path}")
        return False
    
    print(f"✅ Database found: {db_path}")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Check columns exist
        print("\n📋 Checking attendance table columns...")
        cursor.execute("PRAGMA table_info(attendance)")
        columns = [row[1] for row in cursor.fetchall()]
        
        required_columns = ['check_in_time', 'check_out_time', 'hours_worked', 'notes']
        
        for col in required_columns:
            if col in columns:
                print(f"  ✅ Column '{col}' exists")
            else:
                print(f"  ❌ Column '{col}' MISSING!")
                return False
        
        # Check if data exists
        print("\n📊 Checking if data exists...")
        cursor.execute("""
            SELECT COUNT(*) FROM attendance 
            WHERE check_in_time IS NOT NULL AND check_in_time != ''
        """)
        count = cursor.fetchone()[0]
        
        if count > 0:
            print(f"  ✅ Found {count} records with biometric data")
        else:
            print(f"  ❌ NO DATA! Database has 0 records with check-in times")
            print("\n  You need to run: python simple_biometric_fix.py")
            return False
        
        # Show sample data
        print("\n📋 Sample database records:")
        cursor.execute("""
            SELECT date, status, check_in_time, check_out_time, hours_worked, notes
            FROM attendance
            WHERE check_in_time IS NOT NULL
            LIMIT 3
        """)
        
        for row in cursor.fetchall():
            print(f"  Date: {row[0]}, Status: {row[1]}, In: {row[2]}, Out: {row[3]}, Hours: {row[4]}")
        
        return True
        
    finally:
        conn.close()

def check_models():
    """Check if models.py has biometric fields"""
    print()
    print("=" * 80)
    print("  STEP 2: Checking models.py")
    print("=" * 80)
    print()
    
    if not os.path.exists('models.py'):
        print("❌ models.py not found!")
        return False
    
    with open('models.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    if 'check_in_time' in content:
        print("✅ models.py has 'check_in_time' field")
    else:
        print("❌ models.py DOES NOT have 'check_in_time' field!")
        print("\n  You need to add these lines to Attendance class:")
        print("    check_in_time = db.Column(db.String(10))")
        print("    check_out_time = db.Column(db.String(10))")
        print("    hours_worked = db.Column(db.Float)")
        print("    notes = db.Column(db.Text)")
        return False
    
    if 'check_out_time' in content:
        print("✅ models.py has 'check_out_time' field")
    else:
        print("❌ models.py DOES NOT have 'check_out_time' field!")
        return False
    
    if 'hours_worked' in content:
        print("✅ models.py has 'hours_worked' field")
    else:
        print("❌ models.py DOES NOT have 'hours_worked' field!")
        return False
    
    if 'notes' in content and 'db.Column(db.Text)' in content:
        print("✅ models.py has 'notes' field")
    else:
        print("❌ models.py DOES NOT have 'notes' field!")
        return False
    
    return True

def check_backend_code():
    """Check if backend returns biometric data"""
    print()
    print("=" * 80)
    print("  STEP 3: Checking Backend Code (app.py)")
    print("=" * 80)
    print()
    
    if not os.path.exists('app.py'):
        print("❌ app.py not found!")
        return False
    
    with open('app.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check if /my-attendance endpoint exists
    if '/my-attendance' in content:
        print("✅ /my-attendance endpoint exists")
    else:
        print("❌ /my-attendance endpoint NOT FOUND!")
        return False
    
    # Check if it returns biometric fields
    if 'check_in_time' in content and 'att.check_in_time' in content:
        print("✅ Backend returns check_in_time")
    else:
        print("⚠️  Backend might not return check_in_time")
    
    return True

def test_with_app_context():
    """Test reading data using Flask app context"""
    print()
    print("=" * 80)
    print("  STEP 4: Testing with Flask App Context")
    print("=" * 80)
    print()
    
    try:
        # Import Flask app
        sys.path.insert(0, os.getcwd())
        from app import app, db
        from models import Attendance, Employee
        
        with app.app_context():
            print("✅ Successfully imported app and models")
            
            # Try to query attendance
            print("\n📊 Querying attendance records...")
            attendance = Attendance.query.filter(
                Attendance.check_in_time.isnot(None)
            ).first()
            
            if attendance:
                print(f"✅ Found attendance record:")
                print(f"  ID: {attendance.id}")
                print(f"  Date: {attendance.date}")
                print(f"  Status: {attendance.status}")
                
                # Try to access biometric fields
                try:
                    print(f"  Check-in: {attendance.check_in_time}")
                    print(f"  Check-out: {attendance.check_out_time}")
                    print(f"  Hours: {attendance.hours_worked}")
                    print(f"  Notes: {attendance.notes}")
                    print("\n✅ All fields accessible!")
                    return True
                except AttributeError as e:
                    print(f"\n❌ ERROR accessing fields: {e}")
                    print("\n  This means models.py is NOT properly updated!")
                    print("  OR you haven't restarted the backend!")
                    return False
            else:
                print("❌ No attendance records found with check_in_time")
                return False
                
    except ImportError as e:
        print(f"❌ Cannot import Flask app: {e}")
        print("\n  Make sure you're in the backend directory!")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def check_backend_running():
    """Check if backend is running"""
    print()
    print("=" * 80)
    print("  STEP 5: Checking Backend Server")
    print("=" * 80)
    print()
    
    try:
        import requests
        response = requests.get('http://127.0.0.1:5000/', timeout=2)
        print("✅ Backend server is running!")
        return True
    except:
        print("⚠️  Backend server might not be running")
        print("  Start it with: python app.py")
        return False

def main():
    print()
    print("╔" + "=" * 78 + "╗")
    print("║" + " " * 20 + "BIOMETRIC DATA DIAGNOSTIC" + " " * 33 + "║")
    print("╚" + "=" * 78 + "╝")
    print()
    
    results = {
        'database': False,
        'models': False,
        'backend_code': False,
        'flask_test': False,
        'backend_running': False
    }
    
    # Run all checks
    results['database'] = check_database()
    results['models'] = check_models()
    results['backend_code'] = check_backend_code()
    results['flask_test'] = test_with_app_context()
    results['backend_running'] = check_backend_running()
    
    # Summary
    print()
    print("=" * 80)
    print("  DIAGNOSTIC SUMMARY")
    print("=" * 80)
    print()
    
    for check, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status}  {check.replace('_', ' ').title()}")
    
    print()
    print("=" * 80)
    print("  RECOMMENDED ACTIONS")
    print("=" * 80)
    print()
    
    if not results['database']:
        print("🔴 HIGH PRIORITY:")
        print("  1. Run: python simple_biometric_fix.py")
        print("     This will add biometric data to your database")
        print()
    
    if not results['models']:
        print("🔴 HIGH PRIORITY:")
        print("  2. Update models.py with biometric fields")
        print("     Add these lines to Attendance class:")
        print("       check_in_time = db.Column(db.String(10))")
        print("       check_out_time = db.Column(db.String(10))")
        print("       hours_worked = db.Column(db.Float)")
        print("       notes = db.Column(db.Text)")
        print()
    
    if not results['flask_test']:
        print("🟡 IMPORTANT:")
        print("  3. RESTART your backend server")
        print("     Press Ctrl+C to stop, then: python app.py")
        print()
    
    if not results['backend_running']:
        print("🟡 IMPORTANT:")
        print("  4. Make sure backend is running: python app.py")
        print()
    
    if all(results.values()):
        print("🎉 ALL CHECKS PASSED!")
        print()
        print("If data still not showing in frontend:")
        print("  1. Clear browser cache (Ctrl + Shift + Delete)")
        print("  2. Hard refresh (Ctrl + F5)")
        print("  3. Check browser console (F12) for errors")
        print()
    
    print("=" * 80)

if __name__ == "__main__":
    main()
