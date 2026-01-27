# add_temp_password_column.py
from app import app, db
import sqlite3

print("🔧 Adding temp_password column to users table...")

with app.app_context():
    try:
        # Get database path
        db_path = app.config['SQLALCHEMY_DATABASE_URI'].replace('sqlite:///', '')
        
        # Connect to SQLite
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Add the column
        cursor.execute("ALTER TABLE user ADD COLUMN temp_password VARCHAR(100)")
        conn.commit()
        
        print("✅ Column added successfully!")
        
        # Verify
        cursor.execute("PRAGMA table_info(user)")
        columns = cursor.fetchall()
        
        print("\n📋 Current user table columns:")
        for col in columns:
            print(f"   - {col[1]} ({col[2]})")
        
        conn.close()
        
    except sqlite3.OperationalError as e:
        if "duplicate column" in str(e):
            print("⚠️ Column already exists!")
        else:
            print(f"❌ Error: {e}")
    except Exception as e:
        print(f"❌ Error: {e}")

print("\n✅ Done! Restart your Flask server.")