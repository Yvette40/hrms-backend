# ========================================
# QUICK FIX: Add Missing Columns to Database
# Run this to fix the "no such column" error
# ========================================

import sqlite3
import os

# Path to your database
db_path = os.path.join('instance', 'hrms.db')

print("🔧 Adding missing columns to database...")

# Connect to database
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

try:
    # Add missing columns to user table
    print("Adding columns to 'user' table...")
    
    cursor.execute("ALTER TABLE user ADD COLUMN email VARCHAR(120)")
    print("  ✅ Added 'email' column")
    
    cursor.execute("ALTER TABLE user ADD COLUMN phone VARCHAR(20)")
    print("  ✅ Added 'phone' column")
    
    cursor.execute("ALTER TABLE user ADD COLUMN last_login DATETIME")
    print("  ✅ Added 'last_login' column")
    
    conn.commit()
    print("\n✅ User table updated successfully!")
    
except sqlite3.OperationalError as e:
    if "duplicate column name" in str(e):
        print(f"  ⚠️  Column already exists: {e}")
    else:
        print(f"  ❌ Error: {e}")
    conn.rollback()

try:
    # Add missing columns to employee table
    print("\nAdding columns to 'employee' table...")
    
    cursor.execute("ALTER TABLE employee ADD COLUMN department VARCHAR(100) DEFAULT 'General'")
    print("  ✅ Added 'department' column")
    
    cursor.execute("ALTER TABLE employee ADD COLUMN position VARCHAR(100) DEFAULT 'Employee'")
    print("  ✅ Added 'position' column")
    
    cursor.execute("ALTER TABLE employee ADD COLUMN join_date DATE")
    print("  ✅ Added 'join_date' column")
    
    cursor.execute("ALTER TABLE employee ADD COLUMN leave_balance INTEGER DEFAULT 21")
    print("  ✅ Added 'leave_balance' column")
    
    cursor.execute("ALTER TABLE employee ADD COLUMN user_id INTEGER")
    print("  ✅ Added 'user_id' column")
    
    conn.commit()
    print("\n✅ Employee table updated successfully!")
    
except sqlite3.OperationalError as e:
    if "duplicate column name" in str(e):
        print(f"  ⚠️  Column already exists: {e}")
    else:
        print(f"  ❌ Error: {e}")
    conn.rollback()

# Verify the changes
print("\n📊 Verifying 'user' table structure:")
cursor.execute("PRAGMA table_info(user)")
user_columns = cursor.fetchall()
for col in user_columns:
    print(f"  - {col[1]} ({col[2]})")

print("\n📊 Verifying 'employee' table structure:")
cursor.execute("PRAGMA table_info(employee)")
emp_columns = cursor.fetchall()
for col in emp_columns:
    print(f"  - {col[1]} ({col[2]})")

try:
    # Add missing columns to payroll table
    print("\nAdding columns to 'payroll' table...")
    
    cursor.execute("ALTER TABLE payroll ADD COLUMN payment_date DATE")
    print("  ✅ Added 'payment_date' column")
    
    cursor.execute("ALTER TABLE payroll ADD COLUMN payment_method VARCHAR(50)")
    print("  ✅ Added 'payment_method' column")
    
    conn.commit()
    print("\n✅ Payroll table updated successfully!")
    
except sqlite3.OperationalError as e:
    if "duplicate column name" in str(e):
        print(f"  ⚠️  Column already exists: {e}")
    else:
        print(f"  ❌ Error: {e}")
    conn.rollback()

# Verify payroll table
print("\n📊 Verifying 'payroll' table structure:")
cursor.execute("PRAGMA table_info(payroll)")
payroll_columns = cursor.fetchall()
for col in payroll_columns:
    print(f"  - {col[1]} ({col[2]})")

conn.close()

print("\n✅ Database update complete! You can now run your app.")
print("\nNext steps:")
print("1. Run: python app.py")
print("2. Your dashboard should now work!")