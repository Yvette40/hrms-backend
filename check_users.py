import sqlite3
import os

db_path = os.path.join("instance", "hrms.db")
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# See what columns exist in the user table
cursor.execute("PRAGMA table_info(user);")
columns = cursor.fetchall()

print("Columns in 'user' table:")
for col in columns:
    print(col)

conn.close()
