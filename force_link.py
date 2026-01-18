from app import app
from database import db
from models import User, Employee

with app.app_context():
    # 1. Get the user you are logged in as
    user = User.query.filter_by(username='Jjmwangi').first()
    
    # 2. Get the employee you want to see data for
    employee = Employee.query.filter_by(name='John Mwangi').first()

    if not user:
        print("❌ Could not find User 'Jjmwangi'. Check the spelling!")
    if not employee:
        print("❌ Could not find Employee 'John Mwangi'. Check the spelling!")

    if user and employee:
        employee.user_id = user.id
        db.session.commit()
        print(f"✅ SUCCESS: Linked {user.username} (ID: {user.id}) to {employee.name} (ID: {employee.id})")
        print("Now refresh your frontend!")