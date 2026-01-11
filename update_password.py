import os
import sqlite3
from werkzeug.security import generate_password_hash

db_path = os.path.join("instance", "hrms.db")
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

username = "admin"
password = "AdminPass123"

hashed_pw = generate_password_hash(password)
cursor.execute("UPDATE user SET password_hash = ? WHERE username = ?", (hashed_pw, username))
conn.commit()

print(f"✅ Password for {username} updated successfully.")
conn.close()
