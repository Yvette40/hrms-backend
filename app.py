from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import (
    JWTManager, create_access_token, jwt_required, get_jwt_identity
)
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_cors import CORS
import os, sys
sys.path.append(os.path.dirname(__file__))

from middleware.auth import load_current_user
from database import db
from utils.audit_logger import log_audit_action_safe, log_audit_action_enhanced, log_security_event
from utils.sod_checker import check_payroll_separation, SeparationOfDutiesViolation
from models import User, Employee, Attendance, Payroll, AuditTrail, Anomaly, ApprovalRequest, SecurityEvent, SeparationOfDutiesLog
from flask_mail import Mail, Message
from dotenv import load_dotenv
from datetime import datetime, timedelta
from sqlalchemy import extract

# Load environment variables FIRST
load_dotenv()

# Import SMS and Scheduler services
from sms_service import SMSService
from payroll_scheduler import PayrollScheduler

import json

app = Flask(__name__)

from config import Config
app.config.from_object(Config)

# =====================================================
# CORS CONFIGURATION - FIXED
# =====================================================
CORS(app, resources={
    r"/*": {
        "origins": ["http://localhost:3000", "http://127.0.0.1:3000"],
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"],
        "supports_credentials": True,
        "expose_headers": ["Content-Type", "Authorization"]
    }
})

# =====================================================
# CONFIGURATION
# =====================================================
os.makedirs(os.path.join(app.root_path, "instance"), exist_ok=True)
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
db_path = os.path.join(BASE_DIR, "instance", "hrms.db")

app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{db_path}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["JWT_SECRET_KEY"] = "super-secret-key"
app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER')
app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT', 587))
app.config['MAIL_USE_TLS'] = os.getenv('MAIL_USE_TLS', 'True') == 'True'
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_DEFAULT_SENDER')

# Initialize extensions
mail = Mail(app)
db.init_app(app)
jwt = JWTManager(app)

from flask_migrate import Migrate
migrate = Migrate(app, db)

sms_service = SMSService()
payroll_scheduler = PayrollScheduler()

# =====================================================
# Initialize SMS Service and Payroll Scheduler
# =====================================================
# Initialize after jwt and db
# Initialize scheduler after database setup
# This runs once when the app context is created
def initialize_scheduler():
    """Start the payroll scheduler on app startup"""
    try:
        payroll_scheduler.init_app(app, db, sms_service)
        payroll_scheduler.start()
        print("✅ Payroll scheduler started successfully")
    except Exception as e:
        print(f"❌ Failed to start scheduler: {str(e)}")

@app.before_request
def attach_user():
    load_current_user()


@app.route('/test-email-html')
def test_email_html():
    from flask_mail import Message
    try:
        msg = Message(
            subject="HRMS Test Email",
            recipients=["njugunayvette@gmail.com"],
            body="This is a test email from your HRMS system."
        )
        mail.send(msg)
        return {"message": "Test email sent!"}, 200
    except Exception as e:
        return {"message": f"Failed to send email: {str(e)}"}, 500


# =====================================================
# SMS TEST ENDPOINT (Optional - for testing)
# =====================================================
@app.route('/test-sms', methods=['POST'])
@jwt_required()
def test_sms():
    """Test SMS functionality"""
    try:
        data = request.get_json()
        phone = data.get('phone')
        message = data.get('message', 'Test SMS from HRMS')
        
        if not phone:
            return jsonify({"msg": "Phone number required"}), 400
        
        result = sms_service.send_sms(phone, message)
        
        if result['success']:
            return jsonify({
                "msg": "SMS sent successfully",
                "details": result
            }), 200
        else:
            return jsonify({
                "msg": "Failed to send SMS",
                "error": result.get('error')
            }), 500
            
    except Exception as e:
        return jsonify({"msg": f"Error: {str(e)}"}), 500

# =====================================================
# SCHEDULER MANAGEMENT ENDPOINTS (Optional)
# =====================================================
@app.route('/scheduler/status', methods=['GET'])
@jwt_required()
def scheduler_status():
    """Check if scheduler is running"""
    try:
        is_running = payroll_scheduler.is_running()
        return jsonify({
            "running": is_running,
            "jobs": len(payroll_scheduler.get_jobs()) if is_running else 0
        }), 200
    except Exception as e:
        return jsonify({"msg": f"Error: {str(e)}"}), 500


@app.route('/scheduler/trigger-reminders', methods=['POST'])
@jwt_required()
def trigger_reminders():
    """Manually trigger payroll reminders (for testing)"""
    try:
        current_user = get_jwt_identity()
        user = User.query.filter_by(username=current_user).first()
        
        # Only admins can manually trigger
        if user.role != 'Admin':
            return jsonify({"msg": "Unauthorized"}), 403
        
        # Trigger the reminder job manually
        payroll_scheduler.send_payroll_reminders()
        
        return jsonify({
            "msg": "Reminders triggered successfully"
        }), 200
        
    except Exception as e:
        return jsonify({"msg": f"Error: {str(e)}"}), 500

def get_time_ago(dt):
    """Convert datetime to 'time ago' string"""
    now = datetime.utcnow()
    diff = now - dt
    
    if diff.days > 0:
        return f"{diff.days}d ago"
    elif diff.seconds // 3600 > 0:
        return f"{diff.seconds // 3600}h ago"
    elif diff.seconds // 60 > 0:
        return f"{diff.seconds // 60}m ago"
    else:
        return "just now"


def get_notification_icon(notification_type):
    """Get icon emoji for notification type"""
    icons = {
        'approval': '✅',
        'info': '💰',
        'reminder': '📅',
        'alert': '📄',
        'success': '🎉',
        'warning': '⚠️'
    }
    return icons.get(notification_type, 'ℹ️')

# =====================================================
# INITIALIZE DATABASE WITH SEED DATA
# =====================================================
def init_database():
    """Initialize database with seed data"""
    from models import User, Employee, Attendance
    from datetime import datetime, timedelta
    import random
    
    # Create default users
    users_data = [
        {"username": "admin", "password": "AdminPass123", "role": "Admin"},
        {"username": "hr_officer", "password": "OfficerPass123", "role": "HR Officer"},
        {"username": "dept_manager", "password": "DeptPass123", "role": "Department Manager"},
        {"username": "employee", "password": "employee123", "role": "Employee"},
    ]
    
    for user_data in users_data:
        if not User.query.filter_by(username=user_data["username"]).first():
            user = User(username=user_data["username"], role=user_data["role"])
            user.set_password(user_data["password"])
            db.session.add(user)
    
    # Create sample employees
    employees_data = [
        {"name": "John Mwangi", "national_id": "12345678", "base_salary": 50000},
        {"name": "Mary Wanjiku", "national_id": "23456789", "base_salary": 45000},
        {"name": "Peter Omondi", "national_id": "34567890", "base_salary": 55000},
        {"name": "Jane Akinyi", "national_id": "45678901", "base_salary": 48000},
        {"name": "David Kamau", "national_id": "56789012", "base_salary": 60000},
        {"name": "Grace Njeri", "national_id": "67890123", "base_salary": 42000},
        {"name": "James Otieno", "national_id": "78901234", "base_salary": 52000},
        {"name": "Lucy Chebet", "national_id": "89012345", "base_salary": 47000},
        {"name": "Samuel Kipchoge", "national_id": "90123456", "base_salary": 58000},
        {"name": "Rose Wambui", "national_id": "01234567", "base_salary": 44000},
        {"name": "Patrick Mutua", "national_id": "11234568", "base_salary": 51000},
        {"name": "Susan Nyambura", "national_id": "21234569", "base_salary": 46000},
        {"name": "Michael Ochieng", "national_id": "31234560", "base_salary": 54000},
        {"name": "Ann Muthoni", "national_id": "41234561", "base_salary": 49000},
        {"name": "Robert Kariuki", "national_id": "51234562", "base_salary": 56000},
    ]
    
    for emp_data in employees_data:
        if not Employee.query.filter_by(national_id=emp_data["national_id"]).first():
            employee = Employee(
                name=emp_data["name"],
                national_id=emp_data["national_id"],
                base_salary=emp_data["base_salary"]
            )
            db.session.add(employee)
    
    db.session.commit()
    
    # Create attendance records for last 30 days (only if employees exist and no attendance yet)
    if Employee.query.count() > 0 and Attendance.query.count() == 0:
        employees = Employee.query.all()
        today = datetime.now().date()
        
        for employee in employees:
            for days_ago in range(30):
                date = today - timedelta(days=days_ago)
                
                # Skip weekends
                if date.weekday() >= 5:
                    continue
                
                # 90% present, 10% absent
                status = "Present" if random.random() < 0.9 else "Absent"
                
                attendance = Attendance(
                    employee_id=employee.id,
                    date=date,
                    status=status
                )
                db.session.add(attendance)
        
        db.session.commit()


with app.app_context():
    # Create all database tables first
    db.create_all()
    print("✅ Database tables created")
    
    # Then initialize database with seed data
    init_database() 
    
    user_count = User.query.count()  
    employee_count = Employee.query.count()  
    print(f"✅ Database initialized: {user_count} users, {employee_count} employees")
    
    # Initialize and start scheduler
    try:
        payroll_scheduler.init_app(app, db, sms_service)
        payroll_scheduler.start()
        print("✅ Payroll scheduler started successfully")
        
        # List scheduled jobs
        jobs = payroll_scheduler.list_jobs()
        print(f"📅 Scheduled {len(jobs)} jobs:")
        for job in jobs:
            print(f"  - {job['name']}: {job['next_run']}")
    except Exception as e:
        print(f"❌ Failed to start scheduler: {str(e)}")
        import traceback
        traceback.print_exc()


# ROUTES
# =====================================================
@app.route("/")
def home():
    return "✅ HRMS Backend Running Successfully!"

# =====================================================
# AUTHENTICATION
# =====================================================
@app.route("/login", methods=["POST"])
def login():
    data = request.json
    if not data or not data.get("username") or not data.get("password"):
        return jsonify({"msg": "Username and password are required"}), 400

    user = User.query.filter_by(username=data["username"]).first()
    if not user or not user.check_password(data["password"]):
        log_audit_action_safe(
            db,
            action_type="LOGIN_FAILED",
            description=f"Failed login attempt for {data.get('username')}",
            module="AUTH",
            ip_address=request.remote_addr,
        )
        return jsonify({"msg": "Invalid credentials"}), 401

    # Update last login
    user.last_login = datetime.utcnow()
    db.session.commit()

    log_audit_action_safe(
        db,
        action_type="LOGIN_SUCCESS",
        description=f"User {user.username} logged in successfully",
        module="AUTH",
        user_id=user.id,
        ip_address=request.remote_addr,
    )

    access_token = create_access_token(identity=user.username)
    
    # Get linked employee profile if exists
    employee_profile = user.employee_profile
    
    # Build response with role and employee data
    response_data = {
        'access_token': access_token,
        'role': user.role,  # ✅ From database
        'username': user.username,
        'user_id': user.id,
    }
    
    # Add employee details if profile exists
    if employee_profile:
        response_data.update({
            'employee_id': employee_profile.id,
            'employee_national_id': employee_profile.national_id,
            'employee_name': employee_profile.name,
            'department': employee_profile.department or 'General',
            'position': employee_profile.position or 'Employee',
            'email': employee_profile.email or user.email,
            'phone': employee_profile.phone_number or user.phone,
        })
    else:
        # User without employee profile (e.g., Admin, HR Officer)
        response_data.update({
            'employee_id': None,
            'employee_national_id': None,
            'employee_name': user.username,
            'department': 'Administration',
            'position': user.role,  # Fallback to role
            'email': user.email,
            'phone': user.phone,
        })
    
    return jsonify(response_data), 200

# =====================================================
# dashboard MANAGEMENT
# =====================================================
@app.route("/dashboard-stats", methods=["GET"])
@jwt_required()
def dashboard_stats():
    """Enhanced dashboard statistics for all roles"""
    try:
        current_user = get_jwt_identity()
        user = User.query.filter_by(username=current_user).first()
        
        if not user:
            return jsonify({"error": "User not found"}), 404
        
        # Total employees
        total_employees = Employee.query.filter_by(active=True).count()
        
        # Most recent 5 employees
        recent_employees_query = Employee.query.order_by(Employee.id.desc()).limit(5).all()
        recent_employees = [
            {
                "id": e.id,
                "name": e.name,
                "national_id": e.national_id,
                "employee_id": e.id
            }
            for e in recent_employees_query
        ]
        
        # Calculate attendance rate for today
        today = datetime.now().date()
        total_today = Attendance.query.filter_by(date=today).count()
        present_today = Attendance.query.filter_by(date=today, status='Present').count()
        attendance_rate = round((present_today / total_today * 100), 1) if total_today > 0 else 0
        
        # Count pending payroll records
        pending_payroll = Payroll.query.filter_by(status='Pending').count()
        
        # Count pending leave requests
        leave_requests = 0  # TODO: Implement when LeaveRequest model exists
        
        # Count employees on leave today
        on_leave = 0  # TODO: Implement when LeaveRequest model exists
        
        # Count pending approvals
        pending_approvals = ApprovalRequest.query.filter_by(status='Pending').count()
        
        # Department-specific stats (for Department Manager)
        dept_stats = {}
        if user.role == 'Department Manager':
            dept_stats = {
                'deptEmployees': 12,
                'presentToday': 10,
                'onLeave': 2,
                'deptAttendanceRate': 83
            }
        
        # Log the audit action
        log_audit_action_safe(
            db,
            action_type="VIEW_DASHBOARD",
            description="Viewed dashboard stats",
            module="DASHBOARD",
            user_id=user.id,
            ip_address=request.remote_addr
        )
        
        return jsonify({
            "totalEmployees": total_employees,
            "recentEmployees": recent_employees,
            "presentToday": present_today,
            "onLeave": on_leave,
            "pendingApprovals": pending_approvals,
            "pendingPayroll": pending_payroll,
            "leaveRequests": leave_requests,
            "attendanceRate": attendance_rate,
            **dept_stats
        }), 200
        
    except Exception as e:
        print(f"Error in dashboard_stats: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@app.route("/recent-activity", methods=["GET"])
@jwt_required()
def get_recent_activity():
    """Get recent system activity for Admin/HR dashboards"""
    try:
        current_user = get_jwt_identity()
        user = User.query.filter_by(username=current_user).first()
        
        # Only Admin and HR Officer can view activity
        if user.role not in ['Admin', 'HR Officer']:
            return jsonify({'error': 'Unauthorized'}), 403
        
        activities = []
        
        # Get recent audit trail entries
        recent_audits = AuditTrail.query.order_by(
            AuditTrail.timestamp.desc()
        ).limit(10).all()
        
        for audit in recent_audits:
            # Determine activity type
            action_type = 'default'
            if 'PAYROLL' in audit.action.upper():
                action_type = 'payroll'
            elif 'EMPLOYEE' in audit.action.upper():
                action_type = 'employee'
            elif 'USER' in audit.action.upper():
                action_type = 'user'
            
            activities.append({
                'action': audit.details or audit.action,
                'time': get_time_ago(audit.timestamp),
                'type': action_type,
                'timestamp': audit.timestamp.isoformat()
            })
        
        return jsonify(activities), 200
        
    except Exception as e:
        print(f"Error in get_recent_activity: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

# =====================================================
# EMPLOYEE MANAGEMENT
# =====================================================
@app.route("/employees", methods=["POST"])
@jwt_required()
def add_employee():
    current_user = get_jwt_identity()
    user = User.query.filter_by(username=current_user).first()
    
    # Only Admin and HR Officer can add employees
    if user.role not in ['Admin', 'HR Officer']:
        return jsonify({"msg": "Unauthorized"}), 403
    
    data = request.get_json()
    name = data.get("name")
    national_id = data.get("national_id")
    base_salary = data.get("base_salary")
    email = data.get("email")
    phone_number = data.get("phone_number")
    department = data.get("department", "General")
    position = data.get("position", "Employee")
    
    # ✅ NEW: Check if we should create a user account
    create_user_account = data.get("create_user_account", True)
    username = data.get("username")
    temp_password = data.get("temp_password", "TempPass123")

    if not name or not national_id or base_salary is None:
        return jsonify({"msg": "Please provide name, national_id, and base_salary"}), 400

    # Check if employee already exists
    existing = Employee.query.filter_by(national_id=national_id).first()
    if existing:
        return jsonify({"msg": "Employee with this National ID already exists"}), 400

    user_id = None
    created_username = None
    
    # ✅ Create user account if requested
    if create_user_account:
        # Generate username if not provided
        if not username:
            # Auto-generate: first letter + last name (e.g., John Mwangi -> jmwangi)
            name_parts = name.lower().split()
            if len(name_parts) >= 2:
                username = name_parts[0][0] + name_parts[-1]
            else:
                username = name_parts[0]
            
            # Make sure username is unique
            base_username = username
            counter = 1
            while User.query.filter_by(username=username).first():
                username = f"{base_username}{counter}"
                counter += 1
        
        # Check if username already exists
        if User.query.filter_by(username=username).first():
            return jsonify({"msg": f"Username '{username}' already exists"}), 400
        
        # Create user account
        new_user = User(
            username=username,
            role="Employee",
            email=email,
            phone=phone_number
        )
        new_user.set_password(temp_password)
        db.session.add(new_user)
        db.session.flush()  # Get the user ID
        
        user_id = new_user.id
        created_username = username

    # Create employee record
    new_emp = Employee(
        name=name,
        national_id=national_id,
        base_salary=base_salary,
        email=email,
        phone_number=phone_number,
        department=department,
        position=position,
        user_id=user_id  # ✅ Link to user account
    )
    db.session.add(new_emp)
    db.session.commit()

    # Audit log
    log_audit_action_safe(
        db,
        action_type="ADD_EMPLOYEE",
        description=f"Added employee {name}" + (f" with username {created_username}" if created_username else ""),
        module="EMPLOYEE",
        user_id=user.id,
        ip_address=request.remote_addr,
    )
    
    # ✅ TODO: Send email/SMS with credentials
    # send_credentials_email(email, created_username, temp_password)

    response = {
        "msg": "Employee added successfully",
        "employee": {
            "id": new_emp.id,
            "name": new_emp.name,
            "national_id": new_emp.national_id,
            "base_salary": new_emp.base_salary,
            "department": new_emp.department,
            "position": new_emp.position
        }
    }
    
    if created_username:
        response["user_credentials"] = {
            "username": created_username,
            "temp_password": temp_password,
            "message": "⚠️ Save these credentials! Send them to the employee."
        }
    
    return jsonify(response), 201


@app.route("/employees", methods=["GET"])
@jwt_required()
def get_employees():
    current_user = get_jwt_identity()
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 10, type=int)

    employees = Employee.query.paginate(page=page, per_page=per_page, error_out=False)

    log_audit_action_safe(
        db,
        action_type="VIEW_EMPLOYEES",
        description="Viewed employee list",
        module="EMPLOYEE",
        user_id=current_user,
    )

    return jsonify(
        {
            "current_page": employees.page,
            "pages": employees.pages,
            "per_page": employees.per_page,
            "total": employees.total,
            "employees": [
                {
                    "id": e.id,
                    "name": e.name,
                    "national_id": getattr(e, "national_id", ""),
                    "base_salary": e.base_salary,
                    "active": getattr(e, "active", True),  # Safe default
                }
                for e in employees.items
            ],
        }
    )


@app.route("/employees/<int:id>", methods=["PUT"])
@jwt_required()
def update_employee(id):
    current_user = get_jwt_identity()
    user = User.query.filter_by(username=current_user).first()
    emp = Employee.query.get_or_404(id)
    data = request.json

    old_name = emp.name
    emp.name = data.get("name", emp.name)
    emp.national_id = data.get("national_id", emp.national_id)
    emp.base_salary = data.get("base_salary", emp.base_salary)

    db.session.commit()

    log_audit_action_safe(
        db,
        action_type="UPDATE",
        description=f"Updated employee {old_name} → {emp.name}",
        module="EMPLOYEE",
        user_id=user.id,
        ip_address=request.remote_addr,
    )
    return jsonify({"msg": "Employee updated successfully"}), 200


@app.route("/employees/<int:id>", methods=["DELETE"])
@jwt_required()
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

@app.route("/my-info", methods=["GET"])
@jwt_required()
def get_my_info():
    """Get personal information for logged-in employee"""
    try:
        current_user = get_jwt_identity()
        user = User.query.filter_by(username=current_user).first()
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Only Employee role can access this
        if user.role != 'Employee':
            return jsonify({'error': 'This endpoint is for employees only'}), 403
        
        # Find the employee record by matching username to employee name
        employee = Employee.query.filter_by(name=user.username).first()
        
        if not employee:
            return jsonify({
                'employeeId': 'N/A',
                'department': 'Not Assigned',
                'position': user.role,
                'joinDate': 'N/A',
                'daysPresent': 0,
                'leaveBalance': 0,
                'lastPayslip': 'N/A',
                'myAttendanceRate': 0,
                'leaveHistory': []
            }), 200
        
        # Calculate days present this month
        from sqlalchemy import extract
        current_month = datetime.now().month
        current_year = datetime.now().year
        
        days_present = Attendance.query.filter(
            Attendance.employee_id == employee.id,
            Attendance.status == 'Present',
            extract('month', Attendance.date) == current_month,
            extract('year', Attendance.date) == current_year
        ).count()
        
        # Calculate total attendance days this month
        total_days = Attendance.query.filter(
            Attendance.employee_id == employee.id,
            extract('month', Attendance.date) == current_month,
            extract('year', Attendance.date) == current_year
        ).count()
        
        my_attendance_rate = round((days_present / total_days * 100), 1) if total_days > 0 else 0
        
        # Get latest approved payslip
        latest_payslip = Payroll.query.filter_by(
            employee_id=employee.id,
            status='Approved'
        ).order_by(Payroll.period_end.desc()).first()
        
        last_payslip = latest_payslip.period_end.strftime('%b %Y') if latest_payslip else 'N/A'
        
        # Get department and position
        department = getattr(employee, 'department', 'General')
        position = getattr(employee, 'position', 'Employee')
        join_date = getattr(employee, 'join_date', None)
        join_date_str = join_date.strftime('%b %Y') if join_date else 'Jan 2024'
        leave_balance = getattr(employee, 'leave_balance', 21)
        
        return jsonify({
            'employeeId': employee.national_id,
            'department': department,
            'position': position,
            'joinDate': join_date_str,
            'daysPresent': days_present,
            'leaveBalance': leave_balance,
            'lastPayslip': last_payslip,
            'myAttendanceRate': my_attendance_rate,
            'leaveHistory': []
        }), 200
        
    except Exception as e:
        print(f"Error in get_my_info: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

# =====================================================
# ATTENDANCE
# =====================================================
@app.route("/attendance", methods=["POST"])
@jwt_required()
def record_attendance():
    data = request.json
    if not data.get("employee_id") or not data.get("status"):
        return jsonify({"msg": "employee_id and status are required"}), 400

    att = Attendance(
        employee_id=data["employee_id"],
        date=datetime.utcnow(),
        status=data["status"],
    )
    db.session.add(att)
    db.session.commit()

    log_audit_action_safe(
        db,
        action_type="ATTENDANCE_RECORDED",
        description=f"Recorded attendance for employee ID {data['employee_id']}",
        module="ATTENDANCE",
        user_id=get_jwt_identity(),
        ip_address=request.remote_addr,
    )
    return jsonify({"msg": "Attendance recorded successfully"}), 201


# =====================================================
# PAYROLL MANAGEMENT
# =====================================================

# ✅ NEW: GET ALL PAYROLLS ENDPOINT
@app.route("/payrolls", methods=["GET", "OPTIONS"])
@jwt_required(optional=True)  # Allow unauthenticated OPTIONS requests
def get_payrolls():
    """Fetch all payroll records"""
    # Handle OPTIONS preflight request
    if request.method == "OPTIONS":
        return "", 204
    
    try:
        current_user = get_jwt_identity()
        
        # Get all payrolls ordered by most recent
        payrolls = Payroll.query.order_by(Payroll.id.desc()).all()
        
        result = []
        for p in payrolls:
            emp = Employee.query.get(p.employee_id)
            result.append({
                "id": p.id,
                "employee": emp.name if emp else "Unknown",
                "employee_id": p.employee_id,
                "period_start": p.period_start.strftime("%Y-%m-%d"),
                "period_end": p.period_end.strftime("%Y-%m-%d"),
                "gross_salary": float(p.gross_salary),
                "anomaly_flag": p.anomaly_flag,
                "status": getattr(p, 'status', 'Approved'),  # Safe default
                "prepared_by": getattr(p, 'prepared_by', None),
                "approved_by": getattr(p, 'approved_by', None),
                "approved_at": p.approved_at.strftime("%Y-%m-%d %H:%M:%S") if hasattr(p, 'approved_at') and p.approved_at else None
            })
        
        # Log audit action
        if current_user:
            log_audit_action_safe(
                db,
                action_type="VIEW_PAYROLLS",
                description=f"Viewed {len(result)} payroll records",
                module="PAYROLL",
                user_id=current_user,
                ip_address=request.remote_addr,
            )
        
        return jsonify(result), 200
        
    except Exception as e:
        print(f"❌ Error in get_payrolls: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


# =====================================================
# APPROVAL WORKFLOW ENDPOINTS
# =====================================================

  
@app.route("/approval-requests", methods=["GET"])
@jwt_required()
def get_approval_requests():
    """Get pending approvals"""
    requests_list = ApprovalRequest.query.filter_by(status="Pending").all()
    
    result = []
    for req in requests_list:
        requester = User.query.get(req.requested_by)
        result.append({
            "id": req.id,
            "type": req.request_type,
            "reference_id": req.reference_id,
            "requested_by": requester.username if requester else "Unknown",
            "requested_at": req.requested_at.strftime("%Y-%m-%d %H:%M:%S"),
            "status": req.status
        })
    
    return jsonify(result), 200


# =====================================================
# ANOMALY DETECTION
# =====================================================
@app.route("/anomalies/detect", methods=["POST"])
@jwt_required()
def detect_anomalies():
    current_user = get_jwt_identity()
    user = User.query.filter_by(username=current_user).first()
    flagged_payrolls = Payroll.query.filter_by(anomaly_flag=True).all()
    new_anomalies = []

    for p in flagged_payrolls:
        existing = Anomaly.query.filter_by(payroll_id=p.id).first()
        if not existing:
            emp = Employee.query.get(p.employee_id)
            anomaly = Anomaly(
                employee_id=emp.id,
                payroll_id=p.id,
                description=f"No attendance recorded for {emp.name} in payroll period.",
                severity="High",
            )
            db.session.add(anomaly)
            new_anomalies.append(emp.name)

    db.session.commit()

    log_audit_action_safe(
        db,
        action_type="DETECT_ANOMALIES",
        description=f"Detected {len(new_anomalies)} anomalies",
        module="ANOMALY",
        user_id=user.id,
        ip_address=request.remote_addr,
    )
    return jsonify({"msg": f"Detected {len(new_anomalies)} anomalies", "employees": new_anomalies}), 200


@app.route("/anomalies/<int:id>/resolve", methods=["PUT"])
@jwt_required()
def resolve_anomaly(id):
    current_user = get_jwt_identity()
    user = User.query.filter_by(username=current_user).first()
    anomaly = Anomaly.query.get_or_404(id)
    anomaly.resolved = True
    db.session.commit()

    log_audit_action_safe(
        db,
        action_type="RESOLVE_ANOMALY",
        description=f"Marked anomaly {id} as resolved",
        module="ANOMALY",
        user_id=user.id,
        ip_address=request.remote_addr,
    )
    return jsonify({"msg": f"Anomaly {id} resolved successfully"}), 200


# =====================================================
# AUDIT TRAIL ENDPOINT (For frontend fetch)
# =====================================================
from sqlalchemy import and_, func

def parse_date_iso(value):
    if not value:
        return None
    try:
        return datetime.strptime(value, "%Y-%m-%d")
    except ValueError:
        try:
            return datetime.fromisoformat(value)
        except ValueError:
            return None


@app.route("/audit_trail", methods=["GET"])
def get_audit_logs():
    try:
        logs = AuditTrail.query.order_by(AuditTrail.timestamp.desc()).all()

        result = [
            {
                "id": r.id,
                "timestamp": r.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                "user_id": r.user_id,
                "action": r.action,
                "module": r.module,
                "details": r.details,
                "ip_address": r.ip_address
            }
            for r in logs
        ]

        return jsonify(result), 200
    except Exception as e:
        print("Error fetching audit logs:", e)
        return jsonify({"error": str(e)}), 500

def calculate_nssf(gross_salary):
    """Calculate NSSF deduction (6% capped at KES 1,080)"""
    nssf = min(gross_salary * 0.06, 1080)
    return round(nssf, 2)

def calculate_nhif(gross_salary):
    """Calculate NHIF deduction based on salary brackets"""
    if gross_salary <= 5999:
        return 150
    elif gross_salary <= 7999:
        return 300
    elif gross_salary <= 11999:
        return 400
    elif gross_salary <= 14999:
        return 500
    elif gross_salary <= 19999:
        return 600
    elif gross_salary <= 24999:
        return 750
    elif gross_salary <= 29999:
        return 850
    elif gross_salary <= 34999:
        return 900
    elif gross_salary <= 39999:
        return 950
    elif gross_salary <= 44999:
        return 1000
    elif gross_salary <= 49999:
        return 1100
    elif gross_salary <= 59999:
        return 1200
    elif gross_salary <= 69999:
        return 1300
    elif gross_salary <= 79999:
        return 1400
    elif gross_salary <= 89999:
        return 1500
    elif gross_salary <= 99999:
        return 1600
    else:
        return 1700

def calculate_paye(gross_salary, nssf):
    """Calculate PAYE (Pay As You Earn) - Kenyan progressive tax"""
    taxable_income = gross_salary - nssf
    
    if taxable_income <= 24000:
        paye = taxable_income * 0.10
    elif taxable_income <= 32333:
        paye = 2400 + (taxable_income - 24000) * 0.25
    else:
        paye = 4483.25 + (taxable_income - 32333) * 0.30
    
    # Personal relief
    personal_relief = 2400
    paye = max(paye - personal_relief, 0)
    
    return round(paye, 2)

def calculate_housing_levy(gross_salary):
    """Calculate Housing Levy (1.5%)"""
    return round(gross_salary * 0.015, 2)

def calculate_payroll_for_employee(employee, period_start, period_end):
    """Calculate complete payroll for one employee"""
    
    # Get attendance days
    attendance_days = Attendance.query.filter(
        Attendance.employee_id == employee.id,
        Attendance.date >= period_start,
        Attendance.date <= period_end,
        Attendance.status == "Present"
    ).count()
    
    # Basic salary
    gross_salary = float(employee.base_salary)
    
    # Calculate deductions
    nssf = calculate_nssf(gross_salary)
    nhif = calculate_nhif(gross_salary)
    paye = calculate_paye(gross_salary, nssf)
    housing_levy = calculate_housing_levy(gross_salary)
    
    # Total deductions
    total_deductions = nssf + nhif + paye + housing_levy
    
    # Net salary
    net_salary = gross_salary - total_deductions
    
    # Anomaly detection
    anomaly_flag = attendance_days == 0
    
    return {
        'employee_id': employee.id,
        'employee_name': employee.name,
        'gross_salary': gross_salary,
        'nssf': nssf,
        'nhif': nhif,
        'paye': paye,
        'housing_levy': housing_levy,
        'total_deductions': total_deductions,
        'net_salary': net_salary,
        'attendance_days': attendance_days,
        'anomaly_flag': anomaly_flag
    }

# ===================================================
# PAYROLL ENDPOINTS
# ===================================================

@app.route("/payroll/calculate", methods=["POST"])
@jwt_required()
def calculate_payroll_preview():
    """Preview payroll calculation without saving (HR Officer)"""
    current_user = get_jwt_identity()
    user = User.query.filter_by(username=current_user).first()
    
    # Only HR Officer and Admin can calculate
    if user.role not in ['HR Officer', 'Admin']:
        return jsonify({"msg": "Only HR Officer can calculate payroll"}), 403
    
    data = request.json
    try:
        period_start = datetime.strptime(data["period_start"], "%Y-%m-%d").date()
        period_end = datetime.strptime(data["period_end"], "%Y-%m-%d").date()
    except:
        return jsonify({"msg": "Invalid date format. Use YYYY-MM-DD"}), 400
    
    # Get all active employees
    employees = Employee.query.filter_by(active=True).all()
    
    if not employees:
        return jsonify({"msg": "No active employees found"}), 404
    
    payroll_preview = []
    summary = {
        'total_employees': len(employees),
        'total_gross': 0,
        'total_deductions': 0,
        'total_net': 0,
        'anomalies': 0
    }
    
    for emp in employees:
        calc = calculate_payroll_for_employee(emp, period_start, period_end)
        payroll_preview.append(calc)
        
        summary['total_gross'] += calc['gross_salary']
        summary['total_deductions'] += calc['total_deductions']
        summary['total_net'] += calc['net_salary']
        if calc['anomaly_flag']:
            summary['anomalies'] += 1
    
    return jsonify({
        "preview": payroll_preview,
        "summary": summary,
        "period": {
            "start": period_start.strftime("%Y-%m-%d"),
            "end": period_end.strftime("%Y-%m-%d")
        }
    }), 200


@app.route("/payroll/submit", methods=["POST"])
@jwt_required()
def submit_payroll():
    """Submit calculated payroll for approval (HR Officer)"""
    current_user = get_jwt_identity()
    user = User.query.filter_by(username=current_user).first()
    
    # Only HR Officer can submit payroll
    if user.role not in ['HR Officer', 'Admin']:
        return jsonify({"msg": "Only HR Officer can submit payroll"}), 403
    
    data = request.json
    try:
        period_start = datetime.strptime(data["period_start"], "%Y-%m-%d").date()
        period_end = datetime.strptime(data["period_end"], "%Y-%m-%d").date()
    except:
        return jsonify({"msg": "Invalid date format"}), 400
    
    # Check if payroll already exists for this period
    existing = Payroll.query.filter(
        Payroll.period_start == period_start,
        Payroll.period_end == period_end
    ).first()
    
    if existing:
        return jsonify({"msg": "Payroll already exists for this period"}), 400
    
    employees = Employee.query.filter_by(active=True).all()
    payroll_records = []
    
    for emp in employees:
        calc = calculate_payroll_for_employee(emp, period_start, period_end)
        
        payroll = Payroll(
            employee_id=emp.id,
            period_start=period_start,
            period_end=period_end,
            gross_salary=calc['gross_salary'],
            nssf=calc['nssf'],
            nhif=calc['nhif'],
            paye=calc['paye'],
            housing_levy=calc['housing_levy'],
            total_deductions=calc['total_deductions'],
            net_salary=calc['net_salary'],
            attendance_days=calc['attendance_days'],
            anomaly_flag=calc['anomaly_flag'],
            status='Pending',
            prepared_by=user.id
        )
        db.session.add(payroll)
        payroll_records.append(payroll)
    
    db.session.commit()
    
    # Create approval request
    if payroll_records:
        approval = ApprovalRequest(
            request_type='PAYROLL_BATCH',
            reference_id=payroll_records[0].id,
            requested_by=user.id,
            status='Pending',
            details=f"Payroll for {period_start} to {period_end}"
        )
        db.session.add(approval)
        db.session.commit()
    
    # Log audit
    log_audit_action_safe(
        db,
        action_type="SUBMIT_PAYROLL",
        description=f"HR Officer submitted payroll for {len(employees)} employees",
        module="PAYROLL",
        user_id=user.id,
        ip_address=request.remote_addr
    )
    
    return jsonify({
        "msg": "Payroll submitted successfully",
        "employees_count": len(employees),
        "status": "Pending Admin Approval",
        "total_amount": sum(p.net_salary for p in payroll_records)
    }), 201


@app.route("/payroll/approve/<int:payroll_id>", methods=["POST"])
@jwt_required()
def approve_payroll(payroll_id):
    """Approve payroll batch (Admin only)"""
    current_user = get_jwt_identity()
    user = User.query.filter_by(username=current_user).first()
    
    # Only Admin can approve
    if user.role != 'Admin':
        return jsonify({"msg": "Only Admin can approve payroll"}), 403
    
    payroll = Payroll.query.get_or_404(payroll_id)
    
    if payroll.status != 'Pending':
        return jsonify({"msg": f"Payroll is already {payroll.status}"}), 400
    
    # Separation of Duties check
    if payroll.prepared_by == user.id:
        log_security_event(
            db,
            event_type="SOD_VIOLATION",
            description=f"User {user.username} attempted to approve payroll they prepared",
            severity="High",
            user_id=user.id,
            ip_address=request.remote_addr
        )
        return jsonify({
            "msg": "Cannot approve payroll you prepared (Separation of Duties violation)",
            "violation": True
        }), 403
    
    # Approve all payrolls for this period
    period_payrolls = Payroll.query.filter(
        Payroll.period_start == payroll.period_start,
        Payroll.period_end == payroll.period_end,
        Payroll.status == 'Pending'
    ).all()
    
    for p in period_payrolls:
        p.status = 'Approved'
        p.approved_by = user.id
        p.approved_at = datetime.utcnow()
    
    db.session.commit()
    
    # Update approval request
    approval = ApprovalRequest.query.filter_by(
        reference_id=payroll_id,
        request_type='PAYROLL_BATCH'
    ).first()
    if approval:
        approval.status = 'Approved'
        approval.approved_by = user.id
        approval.approved_at = datetime.utcnow()
        db.session.commit()
    
    # Log audit
    log_audit_action_safe(
        db,
        action_type="APPROVE_PAYROLL",
        description=f"Admin approved payroll for {len(period_payrolls)} employees",
        module="PAYROLL",
        user_id=user.id,
        ip_address=request.remote_addr
    )
    
    return jsonify({
        "msg": "Payroll approved successfully",
        "approved_count": len(period_payrolls),
        "total_amount": sum(p.net_salary for p in period_payrolls)
    }), 200


@app.route("/payroll/reject/<int:payroll_id>", methods=["POST"])
@jwt_required()
def reject_payroll(payroll_id):
    """Reject payroll batch (Admin only)"""
    current_user = get_jwt_identity()
    user = User.query.filter_by(username=current_user).first()
    
    if user.role != 'Admin':
        return jsonify({"msg": "Only Admin can reject payroll"}), 403
    
    data = request.json
    reason = data.get('reason', 'No reason provided')
    
    payroll = Payroll.query.get_or_404(payroll_id)
    
    if payroll.status != 'Pending':
        return jsonify({"msg": f"Payroll is already {payroll.status}"}), 400
    
    # Reject all payrolls for this period
    period_payrolls = Payroll.query.filter(
        Payroll.period_start == payroll.period_start,
        Payroll.period_end == payroll.period_end,
        Payroll.status == 'Pending'
    ).all()
    
    for p in period_payrolls:
        p.status = 'Rejected'
        p.approved_by = user.id
        p.approved_at = datetime.utcnow()
    
    db.session.commit()
    
    # Update approval request
    approval = ApprovalRequest.query.filter_by(
        reference_id=payroll_id,
        request_type='PAYROLL_BATCH'
    ).first()
    if approval:
        approval.status = 'Rejected'
        approval.approved_by = user.id
        approval.approved_at = datetime.utcnow()
        approval.rejection_reason = reason
        db.session.commit()
    
    log_audit_action_safe(
        db,
        action_type="REJECT_PAYROLL",
        description=f"Admin rejected payroll. Reason: {reason}",
        module="PAYROLL",
        user_id=user.id,
        ip_address=request.remote_addr
    )
    
    return jsonify({
        "msg": "Payroll rejected",
        "rejected_count": len(period_payrolls),
        "reason": reason
    }), 200


@app.route("/payroll/employee/<int:employee_id>", methods=["GET"])
@jwt_required()
def get_employee_payslips(employee_id):
    """Get all payslips for a specific employee"""
    current_user = get_jwt_identity()
    user = User.query.filter_by(username=current_user).first()
    
    # Employees can only view their own payslips
    if user.role == 'Employee':
        # TODO: Link user to employee record
        # For now, allow if employee_id matches
        pass
    
    payslips = Payroll.query.filter_by(
        employee_id=employee_id,
        status='Approved'
    ).order_by(Payroll.period_start.desc()).all()
    
    result = []
    for p in payslips:
        result.append({
            'id': p.id,
            'period_start': p.period_start.strftime('%Y-%m-%d'),
            'period_end': p.period_end.strftime('%Y-%m-%d'),
            'gross_salary': p.gross_salary,
            'total_deductions': p.total_deductions,
            'net_salary': p.net_salary,
            'status': p.status
        })
    
    return jsonify(result), 200


@app.route("/payroll/payslip/<int:payroll_id>", methods=["GET"])
@jwt_required()
def get_payslip_details(payroll_id):
    """Get detailed payslip for download"""
    current_user = get_jwt_identity()
    user = User.query.filter_by(username=current_user).first()
    
    payslip = Payroll.query.get_or_404(payroll_id)
    employee = Employee.query.get(payslip.employee_id)
    
    # Authorization check
    if user.role == 'Employee':
        # TODO: Check if this is user's own payslip
        pass
    
    return jsonify({
        'payslip_id': payslip.id,
        'employee': {
            'id': employee.id,
            'name': employee.name,
            'national_id': employee.national_id
        },
        'period': {
            'start': payslip.period_start.strftime('%Y-%m-%d'),
            'end': payslip.period_end.strftime('%Y-%m-%d')
        },
        'earnings': {
            'gross_salary': payslip.gross_salary
        },
        'deductions': {
            'nssf': payslip.nssf,
            'nhif': payslip.nhif,
            'paye': payslip.paye,
            'housing_levy': payslip.housing_levy,
            'total': payslip.total_deductions
        },
        'net_salary': payslip.net_salary,
        'attendance_days': payslip.attendance_days,
        'status': payslip.status
    }), 200


# =====================================================
# SCHEDULER MANAGEMENT ENDPOINTS
# =====================================================

@app.route("/scheduler/jobs", methods=["GET"])
@jwt_required()
def get_scheduled_jobs():
    '''Get list of all scheduled jobs'''
    current_user = get_jwt_identity()
    user = User.query.filter_by(username=current_user).first()
    
    if user.role != 'Admin':
        return jsonify({"msg": "Only Admin can view scheduled jobs"}), 403
    
    jobs = payroll_scheduler.list_jobs()
    return jsonify({"jobs": jobs}), 200


@app.route("/scheduler/run/<job_id>", methods=["POST"])
@jwt_required()
def run_job_manually(job_id):
    '''Manually trigger a scheduled job'''
    current_user = get_jwt_identity()
    user = User.query.filter_by(username=current_user).first()
    
    if user.role != 'Admin':
        return jsonify({"msg": "Only Admin can run jobs"}), 403
    
    success = payroll_scheduler.run_job_now(job_id)
    
    if success:
        return jsonify({"msg": f"Job '{job_id}' scheduled to run immediately"}), 200
    else:
        return jsonify({"msg": f"Failed to run job '{job_id}'"}), 400


@app.route("/scheduler/test-sms", methods=["POST"])
@jwt_required()
def test_sms_endpoint():
    '''Test SMS functionality'''
    current_user = get_jwt_identity()
    user = User.query.filter_by(username=current_user).first()
    
    if user.role != 'Admin':
        return jsonify({"msg": "Only Admin can test SMS"}), 403
    
    data = request.json
    phone_number = data.get('phone_number')
    
    if not phone_number:
        return jsonify({"msg": "Phone number required"}), 400
    
    result = sms_service.send_custom_sms(
        phone_number=phone_number,
        message="Test SMS from Glimmer HRMS. Your system is working correctly!"
    )
    
    if result['success']:
        return jsonify({"msg": "Test SMS sent successfully", "details": result}), 200
    else:
        return jsonify({"msg": "Failed to send test SMS", "error": result.get('error')}), 500


@app.route("/payroll/notify-sms/<int:payroll_id>", methods=["POST"])
@jwt_required()
def send_payroll_sms(payroll_id):
    '''Send SMS notification after payroll approval'''
    current_user = get_jwt_identity()
    user = User.query.filter_by(username=current_user).first()
    
    if user.role != 'Admin':
        return jsonify({"msg": "Only Admin can send SMS notifications"}), 403
    
    payroll = Payroll.query.get_or_404(payroll_id)
    employee = Employee.query.get(payroll.employee_id)
    
    # Check if employee has phone number
    phone_number = getattr(employee, 'phone_number', None)
    
    if not phone_number:
        return jsonify({"msg": "Employee phone number not found"}), 400
    
    # Send SMS
    result = sms_service.send_payroll_notification(
        phone_number=phone_number,
        employee_name=employee.name,
        period_start=payroll.period_start.strftime('%Y-%m-%d'),
        period_end=payroll.period_end.strftime('%Y-%m-%d'),
        net_salary=payroll.net_salary
    )
    
    # Log the action
    log_audit_action_safe(
        db,
        action_type="SMS_SENT",
        description=f"SMS notification sent to {employee.name}",
        module="NOTIFICATION",
        user_id=user.id,
        ip_address=request.remote_addr
    )
    
    if result['success']:
        return jsonify({
            "msg": "SMS sent successfully",
            "employee": employee.name,
            "phone": phone_number
        }), 200
    else:
        return jsonify({
            "msg": "Failed to send SMS",
            "error": result.get('error')
        }), 500


@app.route("/payroll/notify-sms-bulk/<int:payroll_batch_id>", methods=["POST"])
@jwt_required()
def send_bulk_sms_notifications(payroll_batch_id):
    '''Send SMS to all employees in payroll batch'''
    current_user = get_jwt_identity()
    user = User.query.filter_by(username=current_user).first()
    
    if user.role != 'Admin':
        return jsonify({"msg": "Only Admin can send bulk SMS"}), 403
    
    # Get first payroll to find the period
    first_payroll = Payroll.query.get_or_404(payroll_batch_id)
    
    # Get all approved payrolls for this period
    payrolls = Payroll.query.filter(
        Payroll.period_start == first_payroll.period_start,
        Payroll.period_end == first_payroll.period_end,
        Payroll.status == 'Approved'
    ).all()
    
    recipients = []
    for p in payrolls:
        emp = Employee.query.get(p.employee_id)
        if hasattr(emp, 'phone_number') and emp.phone_number:
            recipients.append({
                'phone_number': emp.phone_number,
                'employee_name': emp.name,
                'period_start': p.period_start.strftime('%Y-%m-%d'),
                'period_end': p.period_end.strftime('%Y-%m-%d'),
                'net_salary': p.net_salary
            })
    
    if not recipients:
        return jsonify({"msg": "No employees with phone numbers found"}), 400
    
    # Send bulk SMS
    results = sms_service.send_bulk_sms(recipients)
    
    # Log the action
    log_audit_action_safe(
        db,
        action_type="BULK_SMS_SENT",
        description=f"Bulk SMS sent to {len(results['success'])} employees",
        module="NOTIFICATION",
        user_id=user.id,
        ip_address=request.remote_addr
    )
    
    return jsonify({
        "msg": "Bulk SMS completed",
        "success": len(results['success']),
        "failed": len(results['failed']),
        "details": results
    }), 200

# =====================================================
# EMAIL NOTIFICATION ENDPOINTS
# =====================================================
from email_service import EmailService

@app.route("/payroll/notify/<int:payroll_id>", methods=["POST"])
@jwt_required()
def send_payroll_notification(payroll_id):
    """Send email notification after payroll approval"""
    current_user = get_jwt_identity()
    user = User.query.filter_by(username=current_user).first()
    
    if user.role != 'Admin':
        return jsonify({"msg": "Only Admin can send notifications"}), 403
    
    payroll = Payroll.query.get_or_404(payroll_id)
    employee = Employee.query.get(payroll.employee_id)
    
    if not employee.email:
        return jsonify({"msg": "Employee email not found"}), 400
    
    email_service = EmailService()
    success = email_service.send_payroll_notification(
        employee_email=employee.email,
        employee_name=employee.name,
        period_start=payroll.period_start.strftime('%Y-%m-%d'),
        period_end=payroll.period_end.strftime('%Y-%m-%d'),
        net_salary=payroll.net_salary
    )
    
    if success:
        return jsonify({"msg": "Notification sent successfully"}), 200
    else:
        return jsonify({"msg": "Failed to send notification"}), 500


@app.route("/payroll/notify-all/<int:payroll_batch_id>", methods=["POST"])
@jwt_required()
def send_bulk_notifications(payroll_batch_id):
    """Send notifications to all employees in a payroll batch"""
    current_user = get_jwt_identity()
    user = User.query.filter_by(username=current_user).first()
    
    if user.role != 'Admin':
        return jsonify({"msg": "Only Admin can send notifications"}), 403
    
    first_payroll = Payroll.query.get_or_404(payroll_batch_id)
    
    payrolls = Payroll.query.filter(
        Payroll.period_start == first_payroll.period_start,
        Payroll.period_end == first_payroll.period_end,
        Payroll.status == 'Approved'
    ).all()
    
    employee_list = []
    for p in payrolls:
        emp = Employee.query.get(p.employee_id)
        if emp.email:
            employee_list.append({
                'email': emp.email,
                'name': emp.name,
                'period_start': p.period_start.strftime('%Y-%m-%d'),
                'period_end': p.period_end.strftime('%Y-%m-%d'),
                'net_salary': p.net_salary
            })
    
    if not employee_list:
        return jsonify({"msg": "No employees with email addresses found"}), 400
    
    email_service = EmailService()
    results = email_service.send_bulk_payroll_notifications(employee_list)
    
    return jsonify({
        "msg": "Bulk notifications completed",
        "success": len(results['success']),
        "failed": len(results['failed']),
        "details": results
    }), 200

@app.route('/test-email')
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
        # TODO: Create Notification model and fetch from database
        notifications_list = [
            {
                'id': 1,
                'type': 'approval',
                'title': 'Payroll Approved',
                'message': 'Your payroll for December has been approved.',
                'time': '2h ago',
                'read': False,
                'icon': '✅'
            },
            {
                'id': 2,
                'type': 'info',
                'title': 'Salary Processed',
                'message': 'Your salary has been processed successfully.',
                'time': '1d ago',
                'read': False,
                'icon': '💰'
            },
            {
                'id': 3,
                'type': 'reminder',
                'title': 'Attendance Reminder',
                'message': 'Remember to mark your attendance today.',
                'time': '3d ago',
                'read': True,
                'icon': '📅'
            }
        ]
        
        return jsonify(notifications_list), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/notifications/unread-count', methods=['GET'])
@jwt_required()
def get_unread_count():
    """Get count of unread notifications"""
    try:
        # For now, return sample count
        # TODO: Query from database
        count = 2
        return jsonify({'count': count}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/notifications/<int:notification_id>/read', methods=['PUT'])
@jwt_required()
def mark_notification_read(notification_id):
    """Mark a notification as read"""
    try:
        # TODO: Update in database
        return jsonify({'message': 'Notification marked as read'}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/notifications/mark-all-read', methods=['PUT'])
@jwt_required()
def mark_all_notifications_read():
    """Mark all notifications as read"""
    try:
        # TODO: Update all in database
        return jsonify({'message': 'All notifications marked as read'}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/notifications/<int:notification_id>', methods=['DELETE'])
@jwt_required()
def delete_notification(notification_id):
    """Delete a notification"""
    try:
        # TODO: Delete from database
        return jsonify({'message': 'Notification deleted'}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/user/profile', methods=['GET'])
@jwt_required()
def get_profile():
    """Get user profile"""
    try:
        current_user = get_jwt_identity()
        user = User.query.filter_by(username=current_user).first()
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Get associated employee data if exists
        employee = Employee.query.filter_by(name=user.username).first()
        
        profile = {
            'firstName': user.username.split()[0] if ' ' in user.username else user.username,
            'lastName': user.username.split()[1] if ' ' in user.username else '',
            'email': getattr(user, 'email', 'user@example.com'),
            'phone': getattr(user, 'phone', '+254 712 345 678'),
            'department': getattr(user, 'department', 'Engineering'),
            'position': user.role,
            'employeeId': getattr(employee, 'national_id', 'EMP-001') if employee else 'EMP-001',
            'dateJoined': 'January 15, 2024',
            'address': getattr(user, 'address', 'Nairobi, Kenya'),
            'emergencyContact': getattr(user, 'emergency_contact', '+254 722 111 222'),
            'emergencyName': getattr(user, 'emergency_name', 'Jane Doe')
        }
        
        return jsonify(profile), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/user/profile', methods=['PUT'])
@jwt_required()
def update_profile():
    """Update user profile"""
    try:
        current_user = get_jwt_identity()
        user = User.query.filter_by(username=current_user).first()
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        data = request.get_json()
        
        # Update fields if they exist in User model
        # For now, we'll just acknowledge the update
        # TODO: Add these fields to User model if needed
        
        log_audit_action_safe(
            db,
            action_type="UPDATE_PROFILE",
            description=f"User {user.username} updated their profile",
            module="PROFILE",
            user_id=user.id,
            ip_address=request.remote_addr
        )
        
        return jsonify({'message': 'Profile updated successfully'}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# =====================================================
# SETTINGS ENDPOINTS
# =====================================================

@app.route('/api/user/settings', methods=['GET'])
@jwt_required()
def get_settings():
    """Get user settings"""
    try:
        current_user = get_jwt_identity()
        user = User.query.filter_by(username=current_user).first()
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Return default settings for now
        # TODO: Create UserSettings model and fetch from database
        settings = {
            'emailNotifications': True,
            'pushNotifications': True,
            'smsNotifications': False,
            'leaveRequests': True,
            'payrollAlerts': True,
            'attendanceReminders': True,
            'twoFactorAuth': False,
            'sessionTimeout': '30',
            'theme': 'light',
            'language': 'en',
            'dateFormat': 'MM/DD/YYYY',
            'timeFormat': '12h'
        }
        
        return jsonify(settings), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/user/settings', methods=['PUT'])
@jwt_required()
def update_settings():
    """Update user settings"""
    try:
        current_user = get_jwt_identity()
        user = User.query.filter_by(username=current_user).first()
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        data = request.get_json()
        
        # TODO: Save settings to database
        
        log_audit_action_safe(
            db,
            action_type="UPDATE_SETTINGS",
            description=f"User {user.username} updated their settings",
            module="SETTINGS",
            user_id=user.id,
            ip_address=request.remote_addr
        )
        
        return jsonify({'message': 'Settings updated successfully'}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/user/change-password', methods=['POST'])
@jwt_required()
def change_password():
    """Change user password"""
    try:
        current_user = get_jwt_identity()
        user = User.query.filter_by(username=current_user).first()
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        data = request.get_json()
        
        current_password = data.get('currentPassword')
        new_password = data.get('newPassword')
        
        if not current_password or not new_password:
            return jsonify({'error': 'Both current and new password are required'}), 400
        
        # Verify current password
        if not user.check_password(current_password):
            log_security_event(
                db,
                event_type="PASSWORD_CHANGE_FAILED",
                description=f"Failed password change attempt for {user.username}",
                severity="Medium",
                user_id=user.id,
                ip_address=request.remote_addr
            )
            return jsonify({'error': 'Current password is incorrect'}), 401
        
        # Update password
        user.set_password(new_password)
        db.session.commit()
        
        log_audit_action_safe(
            db,
            action_type="PASSWORD_CHANGED",
            description=f"User {user.username} changed their password",
            module="SECURITY",
            user_id=user.id,
            ip_address=request.remote_addr
        )
        
        return jsonify({'message': 'Password changed successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
    


@app.route("/leave-requests", methods=["GET"])
@jwt_required()
def get_leave_requests():
    """Get all leave requests (Admin/HR can see all, Employee sees only their own)"""
    current_user = get_jwt_identity()
    user = User.query.filter_by(username=current_user).first()
    
    # For now, return empty list (you'll implement LeaveRequest model later)
    # TODO: Implement when LeaveRequest model is created
    
    return jsonify([]), 200


@app.route("/leave-requests/<int:leave_id>/approve", methods=["POST"])
@jwt_required()
def approve_leave_request(leave_id):
    """Approve a leave request (Admin/HR only)"""
    current_user = get_jwt_identity()
    user = User.query.filter_by(username=current_user).first()
    
    if user.role not in ['Admin', 'HR Officer']:
        return jsonify({"msg": "Unauthorized"}), 403
    
    # TODO: Implement when LeaveRequest model is created
    # leave = LeaveRequest.query.get_or_404(leave_id)
    # leave.status = 'Approved'
    # leave.approved_by = user.id
    # leave.approved_at = datetime.utcnow()
    # db.session.commit()
    
    return jsonify({"msg": "Leave request approved"}), 200


@app.route("/leave-requests/<int:leave_id>/reject", methods=["POST"])
@jwt_required()
def reject_leave_request(leave_id):
    """Reject a leave request (Admin/HR only)"""
    current_user = get_jwt_identity()
    user = User.query.filter_by(username=current_user).first()
    
    if user.role not in ['Admin', 'HR Officer']:
        return jsonify({"msg": "Unauthorized"}), 403
    
    data = request.json
    reason = data.get('reason', 'No reason provided')
    
    # TODO: Implement when LeaveRequest model is created
    # leave = LeaveRequest.query.get_or_404(leave_id)
    # leave.status = 'Rejected'
    # leave.approved_by = user.id
    # leave.approved_at = datetime.utcnow()
    # leave.rejection_reason = reason
    # db.session.commit()
    
    return jsonify({"msg": "Leave request rejected"}), 200


@app.route("/leave-requests", methods=["POST"])
@jwt_required()
def create_leave_request():
    """Create a new leave request (Employee)"""
    current_user = get_jwt_identity()
    user = User.query.filter_by(username=current_user).first()
    
    data = request.json
    
    # TODO: Implement when LeaveRequest model is created
    # leave = LeaveRequest(
    #     employee_id=data['employee_id'],
    #     start_date=datetime.strptime(data['start_date'], '%Y-%m-%d').date(),
    #     end_date=datetime.strptime(data['end_date'], '%Y-%m-%d').date(),
    #     leave_type=data.get('leave_type', 'Annual'),
    #     reason=data.get('reason', ''),
    #     status='Pending'
    # )
    # db.session.add(leave)
    # db.session.commit()
    
    return jsonify({"msg": "Leave request created"}), 201


# =====================================================
# USER MANAGEMENT ENDPOINTS (Admin only)
# =====================================================

@app.route("/users", methods=["GET"])
@jwt_required()
def get_users():
    """Get all users (Admin only)"""
    current_user = get_jwt_identity()
    user = User.query.filter_by(username=current_user).first()
    
    if user.role != 'Admin':
        return jsonify({"msg": "Only Admin can view users"}), 403
    
    users = User.query.all()
    
    result = []
    for u in users:
        result.append({
            'id': u.id,
            'username': u.username,
            'role': u.role,
            'is_active': u.is_active,
            'created_at': u.created_at.strftime('%Y-%m-%d %H:%M:%S') if u.created_at else None
        })
    
    return jsonify(result), 200


@app.route("/users", methods=["POST"])
@jwt_required()
def create_user():
    """Create a new user (Admin only)"""
    current_user = get_jwt_identity()
    user = User.query.filter_by(username=current_user).first()
    
    if user.role != 'Admin':
        return jsonify({"msg": "Only Admin can create users"}), 403
    
    data = request.json
    
    # Check if username already exists
    if User.query.filter_by(username=data['username']).first():
        return jsonify({"msg": "Username already exists"}), 400
    
    new_user = User(
        username=data['username'],
        role=data['role']
    )
    new_user.set_password(data['password'])
    
    db.session.add(new_user)
    db.session.commit()
    
    log_audit_action_safe(
        db,
        action_type="CREATE_USER",
        description=f"Created new user: {data['username']}",
        module="USER_MGMT",
        user_id=user.id,
        ip_address=request.remote_addr
    )
    
    return jsonify({"msg": "User created successfully"}), 201


@app.route("/users/<int:user_id>", methods=["PUT"])
@jwt_required()
def update_user(user_id):
    """Update a user (Admin only)"""
    current_user = get_jwt_identity()
    admin_user = User.query.filter_by(username=current_user).first()
    
    if admin_user.role != 'Admin':
        return jsonify({"msg": "Only Admin can update users"}), 403
    
    user_to_update = User.query.get_or_404(user_id)
    data = request.json
    
    # Update fields
    if 'username' in data:
        user_to_update.username = data['username']
    if 'role' in data:
        user_to_update.role = data['role']
    if 'password' in data and data['password']:
        user_to_update.set_password(data['password'])
    
    db.session.commit()
    
    log_audit_action_safe(
        db,
        action_type="UPDATE_USER",
        description=f"Updated user: {user_to_update.username}",
        module="USER_MGMT",
        user_id=admin_user.id,
        ip_address=request.remote_addr
    )
    
    return jsonify({"msg": "User updated successfully"}), 200


@app.route("/users/<int:user_id>", methods=["DELETE"])
@jwt_required()
def delete_user(user_id):
    """Delete a user (Admin only)"""
    current_user = get_jwt_identity()
    admin_user = User.query.filter_by(username=current_user).first()
    
    if admin_user.role != 'Admin':
        return jsonify({"msg": "Only Admin can delete users"}), 403
    
    # Prevent self-deletion
    if user_id == admin_user.id:
        return jsonify({"msg": "Cannot delete your own account"}), 400
    
    user_to_delete = User.query.get_or_404(user_id)
    username = user_to_delete.username
    
    db.session.delete(user_to_delete)
    db.session.commit()
    
    log_audit_action_safe(
        db,
        action_type="DELETE_USER",
        description=f"Deleted user: {username}",
        module="USER_MGMT",
        user_id=admin_user.id,
        ip_address=request.remote_addr
    )
    
    return jsonify({"msg": "User deleted successfully"}), 200


# =====================================================
# EMPLOYEE PAYSLIPS ENDPOINTS
# =====================================================

@app.route("/my-payslips", methods=["GET"])
@jwt_required()
def get_my_payslips():
    """Get payslips for logged-in employee"""
    current_user = get_jwt_identity()
    user = User.query.filter_by(username=current_user).first()
    
    # Find employee record
    employee = Employee.query.filter_by(name=user.username).first()
    
    if not employee:
        return jsonify([]), 200
    
    # Get all approved payslips for this employee
    payslips = Payroll.query.filter_by(
        employee_id=employee.id,
        status='Approved'
    ).order_by(Payroll.period_end.desc()).all()
    
    result = []
    for p in payslips:
        result.append({
            'id': p.id,
            'period_start': p.period_start.strftime('%b %d, %Y'),
            'period_end': p.period_end.strftime('%b %d, %Y'),
            'gross_salary': float(p.gross_salary),
            'total_deductions': float(p.total_deductions),
            'net_salary': float(p.net_salary),
            'status': p.status
        })
    
    return jsonify(result), 200


# Note: /payroll/payslip/<int:payroll_id> endpoint already exists in your app.py


# =====================================================
# ATTENDANCE - MY ATTENDANCE ENDPOINT
# =====================================================

@app.route("/my-attendance", methods=["GET"])
@jwt_required()
def get_my_attendance():
    """Get attendance records for logged-in employee"""
    current_user = get_jwt_identity()
    user = User.query.filter_by(username=current_user).first()
    
    # Find employee record
    employee = Employee.query.filter_by(name=user.username).first()
    
    if not employee:
        return jsonify([]), 200
    
    # Get attendance records (last 30 days)
    from datetime import datetime, timedelta
    thirty_days_ago = datetime.now().date() - timedelta(days=30)
    
    attendance_records = Attendance.query.filter(
        Attendance.employee_id == employee.id,
        Attendance.date >= thirty_days_ago
    ).order_by(Attendance.date.desc()).all()
    
    result = []
    for att in attendance_records:
        result.append({
            'id': att.id,
            'date': att.date.strftime('%Y-%m-%d'),
            'status': att.status,
            'day_of_week': att.date.strftime('%A')
        })
    
    # Calculate stats
    total_days = len(attendance_records)
    present_days = len([a for a in attendance_records if a.status == 'Present'])
    attendance_rate = round((present_days / total_days * 100), 1) if total_days > 0 else 0
    
    return jsonify({
        'records': result,
        'stats': {
            'total_days': total_days,
            'present_days': present_days,
            'absent_days': total_days - present_days,
            'attendance_rate': attendance_rate
        }
    }), 200

@app.route("/check-roles", methods=["GET"])
def check_roles():
    """Check all user roles"""
    users = User.query.all()
    result = []
    for user in users:
        result.append({
            'username': user.username,
            'role': user.role
        })
    return jsonify(result), 200

# =====================================================
# MAIN
# =====================================================

if __name__ == "__main__":
    app.run(debug=True, port=5000)