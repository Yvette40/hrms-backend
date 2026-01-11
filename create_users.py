# ========================================
# FILE: create_users.py
# PURPOSE: Create multiple users with different roles
# RUN THIS AFTER: python app.py (first time)
# ========================================

from app import app, db
from models import User

def create_demo_users():
    """Create demo users for all roles"""
    
    with app.app_context():
        # Check if users already exist
        existing_users = User.query.all()
        if len(existing_users) > 1:
            print("⚠️  Demo users already exist. Skipping creation.")
            return
        
        # Define users with different roles
        users = [
            {
                "username": "admin",
                "password": "AdminPass123",
                "role": "Admin",
                "description": "Full system access - can manage everything"
            },
            {
                "username": "hr_manager",
                "password": "HrPass123",
                "role": "HR Manager",
                "description": "Can manage employees, attendance, payroll, view audit logs"
            },
            {
                "username": "hr_officer",
                "password": "OfficerPass123",
                "role": "HR Officer",
                "description": "Can add employees, mark attendance, view reports"
            },
            {
                "username": "employee",
                "password": "EmpPass123",
                "role": "Employee",
                "description": "View own profile, attendance, and payslips only"
            }
        ]
        
        print("\n" + "="*60)
        print("🔐 CREATING DEMO USERS WITH ROLE-BASED ACCESS")
        print("="*60 + "\n")
        
        for user_data in users:
            # Check if user exists
            existing = User.query.filter_by(username=user_data["username"]).first()
            
            if existing:
                print(f"⏭️  User '{user_data['username']}' already exists. Skipping.")
                continue
            
            # Create new user
            new_user = User(
                username=user_data["username"],
                role=user_data["role"]
            )
            new_user.set_password(user_data["password"])
            
            db.session.add(new_user)
            db.session.commit()
            
            print(f"✅ Created: {user_data['username']}")
            print(f"   Role: {user_data['role']}")
            print(f"   Password: {user_data['password']}")
            print(f"   Access: {user_data['description']}")
            print()
        
        print("="*60)
        print("🎯 USER CREATION COMPLETE!")
        print("="*60)
        print("\n📋 LOGIN CREDENTIALS SUMMARY:\n")
        
        all_users = User.query.all()
        for user in all_users:
            print(f"Role: {user.role:15} | Username: {user.username:15} | Password: Check above")
        
        print("\n" + "="*60)
        print("🚀 You can now login with any of these accounts!")
        print("="*60 + "\n")

if __name__ == "__main__":
    create_demo_users()


# ========================================
# FILE: middleware/role_checker.py
# PURPOSE: Role-based authorization decorator
# ========================================

from functools import wraps
from flask import jsonify
from flask_jwt_extended import get_jwt_identity
from models import User

def role_required(*allowed_roles):
    """
    Decorator to check if user has required role
    
    Usage:
        @app.route('/admin-only')
        @jwt_required()
        @role_required('Admin')
        def admin_page():
            return "Admin content"
    """
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            current_username = get_jwt_identity()
            user = User.query.filter_by(username=current_username).first()
            
            if not user:
                return jsonify({"msg": "User not found"}), 404
            
            if user.role not in allowed_roles:
                return jsonify({
                    "msg": f"Access denied. Required role: {', '.join(allowed_roles)}",
                    "your_role": user.role
                }), 403
            
            return fn(*args, **kwargs)
        return wrapper
    return decorator


# ========================================
# UPDATED: app.py (Add role-based endpoints)
# ========================================

"""
Add these imports at the top of app.py:
"""
from middleware.role_checker import role_required

"""
Add this endpoint to get current user info:
"""

@app.route("/current-user", methods=["GET"])
@jwt_required()
def get_current_user():
    """Get current logged-in user details"""
    current_username = get_jwt_identity()
    user = User.query.filter_by(username=current_username).first()
    
    if not user:
        return jsonify({"msg": "User not found"}), 404
    
    return jsonify({
        "id": user.id,
        "username": user.username,
        "role": user.role,
        "created_at": user.created_at.strftime("%Y-%m-%d %H:%M:%S")
    }), 200


"""
Example: Protect employee deletion to Admin only
"""

@app.route("/employees/<int:id>", methods=["DELETE"])
@jwt_required()
@role_required("Admin", "HR Manager")  # Only Admin and HR Manager can delete
def delete_employee(id):
    current_user = get_jwt_identity()
    user = User.query.filter_by(username=current_user).first()
    emp = Employee.query.get_or_404(id)
    emp_name = emp.name

    db.session.delete(emp)
    db.session.commit()

    log_audit_action_safe(
        db,
        action_type="DELETE",
        description=f"Deleted employee {emp_name}",
        module="EMPLOYEE",
        user_id=user.id,
        ip_address=request.remote_addr,
    )
    return jsonify({"msg": "Employee deleted successfully"}), 200


"""
Example: Restrict payroll to Admin and HR Manager only
"""

@app.route("/payroll/run", methods=["POST"])
@jwt_required()
@role_required("Admin", "HR Manager")  # Only these roles can process payroll
def run_payroll():
    current_user = get_jwt_identity()
    user = User.query.filter_by(username=current_user).first()
    data = request.json

    start = datetime.strptime(data["period_start"], "%Y-%m-%d")
    end = datetime.strptime(data["period_end"], "%Y-%m-%d")
    employees = Employee.query.filter_by(active=True).all()
    payrolls = []

    for e in employees:
        attendance_days = Attendance.query.filter(
            Attendance.employee_id == e.id,
            Attendance.date >= start,
            Attendance.date <= end,
            Attendance.status == "Present",
        ).count()

        anomaly = attendance_days == 0
        gross = e.base_salary

        p = Payroll(
            employee_id=e.id,
            period_start=start,
            period_end=end,
            gross_salary=gross,
            anomaly_flag=anomaly,
        )
        db.session.add(p)
        payrolls.append({
            "employee": e.name,
            "gross_salary": gross,
            "attendance_days": attendance_days,
            "anomaly_flag": anomaly,
        })

    db.session.commit()

    log_audit_action_safe(
        db,
        action_type="RUN_PAYROLL",
        description=f"Processed payroll for {len(employees)} employees",
        module="PAYROLL",
        user_id=user.id,
        ip_address=request.remote_addr,
    )

    return jsonify({"msg": "Payroll processed", "data": payrolls}), 200


# ========================================
# ROLE PERMISSIONS MATRIX
# ========================================

"""
┌─────────────────┬───────┬────────────┬────────────┬──────────┐
│ Feature         │ Admin │ HR Manager │ HR Officer │ Employee │
├─────────────────┼───────┼────────────┼────────────┼──────────┤
│ View Dashboard  │  ✅   │     ✅     │     ✅     │    ✅    │
│ Add Employee    │  ✅   │     ✅     │     ✅     │    ❌    │
│ Edit Employee   │  ✅   │     ✅     │     ✅     │    ❌    │
│ Delete Employee │  ✅   │     ✅     │     ❌     │    ❌    │
│ Mark Attendance │  ✅   │     ✅     │     ✅     │    ❌    │
│ View Attendance │  ✅   │     ✅     │     ✅     │    ✅*   │
│ Run Payroll     │  ✅   │     ✅     │     ❌     │    ❌    │
│ View Payroll    │  ✅   │     ✅     │     ✅     │    ✅*   │
│ View Audit Log  │  ✅   │     ✅     │     ❌     │    ❌    │
│ Manage Users    │  ✅   │     ❌     │     ❌     │    ❌    │
└─────────────────┴───────┴────────────┴────────────┴──────────┘

* Employee can only view their OWN data
"""