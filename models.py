# ==============================================================================
# FILE: models.py (ENHANCED FOR DASHBOARD)
# All classes with dashboard-ready fields
# ==============================================================================

from datetime import datetime
from database import db
from werkzeug.security import generate_password_hash, check_password_hash

# =======================
# USERS (Enhanced with additional fields)
# =======================
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(20), default='employee')
    
    # 🆕 Additional user fields
    email = db.Column(db.String(120))
    phone = db.Column(db.String(20))
    is_active = db.Column(db.Boolean, default=True)
    last_login = db.Column(db.DateTime)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


# =======================
# EMPLOYEE (Enhanced with dashboard fields)
# =======================
class Employee(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    national_id = db.Column(db.String(50), unique=True, nullable=False)
    base_salary = db.Column(db.Float, nullable=False)
    
    # 🆕 Dashboard fields
    department = db.Column(db.String(100), default='General')
    position = db.Column(db.String(100), default='Employee')
    email = db.Column(db.String(120))
    phone_number = db.Column(db.String(20))
    join_date = db.Column(db.Date, default=datetime.now().date)
    leave_balance = db.Column(db.Integer, default=21)  # Annual leave days
    address = db.Column(db.String(200)) 
    emergency_name = db.Column(db.String(100))  # ✅ Add back if needed
    emergency_contact = db.Column(db.String(20))

    active = db.Column(db.Boolean, default=True)
    
    # 🆕 Link to user account (for Employee role)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user_account = db.relationship('User', foreign_keys=[user_id], backref='employee_profile')

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "national_id": self.national_id,
            "base_salary": self.base_salary,
            "department": self.department,
            "position": self.position,
            "email": self.email,
            "phone_number": self.phone_number,
            "join_date": self.join_date.strftime('%Y-%m-%d') if self.join_date else None,
            "leave_balance": self.leave_balance,
            "active": self.active
        }


# =======================
# ATTENDANCE
# =======================
class Attendance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employee.id'))
    date = db.Column(db.Date, nullable=False)
    status = db.Column(db.String(20), nullable=False)
    recorded_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Biometric time tracking fields
    check_in_time = db.Column(db.String(10))  # Format: HH:MM
    check_out_time = db.Column(db.String(10))  # Format: HH:MM
    hours_worked = db.Column(db.Float)
    notes = db.Column(db.Text)
    
    # Relationships
    employee = db.relationship('Employee', backref='attendances')


# =======================
# PAYROLL (COMPLETE VERSION)
# =======================
class Payroll(db.Model):
    __tablename__ = 'payroll'
    
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employee.id'), nullable=False)
    
    # Period
    period_start = db.Column(db.Date, nullable=False)
    period_end = db.Column(db.Date, nullable=False)
    
    # Earnings
    gross_salary = db.Column(db.Float, nullable=False)
    
    # Deductions (Kenyan payroll)
    nssf = db.Column(db.Float, default=0)  # National Social Security Fund
    nhif = db.Column(db.Float, default=0)  # National Hospital Insurance Fund
    paye = db.Column(db.Float, default=0)  # Pay As You Earn (Tax)
    housing_levy = db.Column(db.Float, default=0)  # Housing Development Levy
    total_deductions = db.Column(db.Float, default=0)
    
    # Net Pay
    net_salary = db.Column(db.Float, nullable=False)
    
    # Attendance
    attendance_days = db.Column(db.Integer, default=0)
    
    # Anomaly Detection
    anomaly_flag = db.Column(db.Boolean, default=False)
    
    # Approval Workflow (Separation of Duties)
    status = db.Column(db.String(20), default='Pending')  # Pending, Approved, Rejected
    prepared_by = db.Column(db.Integer, db.ForeignKey('user.id'))  # HR Officer
    approved_by = db.Column(db.Integer, db.ForeignKey('user.id'))  # Admin
    approved_at = db.Column(db.DateTime)
    
    # 🆕 Additional fields
    payment_date = db.Column(db.Date)
    payment_method = db.Column(db.String(50))  # Bank Transfer, Cash, Mobile Money
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    employee = db.relationship('Employee', backref='payrolls')
    preparer = db.relationship('User', foreign_keys=[prepared_by], backref='prepared_payrolls')
    approver = db.relationship('User', foreign_keys=[approved_by], backref='approved_payrolls')
    
    def __repr__(self):
        return f'<Payroll {self.id} - Employee {self.employee_id} - {self.period_start} to {self.period_end}>'
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'employee_id': self.employee_id,
            'period_start': self.period_start.strftime('%Y-%m-%d'),
            'period_end': self.period_end.strftime('%Y-%m-%d'),
            'gross_salary': float(self.gross_salary),
            'nssf': float(self.nssf),
            'nhif': float(self.nhif),
            'paye': float(self.paye),
            'housing_levy': float(self.housing_levy),
            'total_deductions': float(self.total_deductions),
            'net_salary': float(self.net_salary),
            'attendance_days': self.attendance_days,
            'anomaly_flag': self.anomaly_flag,
            'status': self.status,
            'prepared_by': self.prepared_by,
            'approved_by': self.approved_by,
            'approved_at': self.approved_at.strftime('%Y-%m-%d %H:%M:%S') if self.approved_at else None,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S')
        }


# =======================
# 🆕 LEAVE REQUESTS (NEW MODEL)
# =======================
class LeaveRequest(db.Model):
    """Tracks employee leave requests"""
    __tablename__ = 'leave_request' # Or 'leave_requests', just be consistent
    
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employee.id'), nullable=False)
    
    # Leave details
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    leave_type = db.Column(db.String(50), default='Annual')
    reason = db.Column(db.Text)
    days_requested = db.Column(db.Integer)
    
    # Approval workflow
    status = db.Column(db.String(20), default='Pending')
    requested_at = db.Column(db.DateTime, default=datetime.utcnow) # <--- THIS IS THE FIELD THE SCRIPT NEEDS
    approved_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    approved_at = db.Column(db.DateTime)
    rejection_reason = db.Column(db.Text)
    
    # Relationships
    employee = db.relationship('Employee', backref='leave_requests_rel') # Changed backref name to avoid conflict
    approver = db.relationship('User', foreign_keys=[approved_by])
    def __repr__(self):
        return f'<LeaveRequest {self.employee_id} - {self.status}>'
    
    def calculate_days(self):
        """Calculate number of leave days"""
        if self.start_date and self.end_date:
            delta = self.end_date - self.start_date
            return delta.days + 1
        return 0
    
    def to_dict(self):
        """Convert leave request to dictionary"""
        return {
            'id': self.id,
            'employee_id': self.employee_id,
            'employee_name': self.employee.name if self.employee else None,
            'start_date': self.start_date.strftime('%Y-%m-%d'),
            'end_date': self.end_date.strftime('%Y-%m-%d'),
            'leave_type': self.leave_type,
            'reason': self.reason,
            'days_requested': self.days_requested or self.calculate_days(),
            'status': self.status,
            'requested_at': self.requested_at.strftime('%Y-%m-%d %H:%M:%S'),
            'approved_at': self.approved_at.strftime('%Y-%m-%d %H:%M:%S') if self.approved_at else None,
            'rejection_reason': self.rejection_reason
        }


# =======================
# APPROVAL REQUESTS
# =======================
class ApprovalRequest(db.Model):
    """Tracks all approval workflows in the system"""
    __tablename__ = "approval_request"
    
    id = db.Column(db.Integer, primary_key=True)
    request_type = db.Column(db.String(50), nullable=False)
    reference_id = db.Column(db.Integer, nullable=False)
    
    # Workflow tracking
    requested_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    approved_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    status = db.Column(db.String(20), default='Pending')
    
    # Details
    request_data = db.Column(db.Text)
    comments = db.Column(db.Text)
    rejection_reason = db.Column(db.Text)
    details = db.Column(db.Text)
    
    # Timestamps
    requested_at = db.Column(db.DateTime, default=datetime.utcnow)
    reviewed_at = db.Column(db.DateTime)
    approved_at = db.Column(db.DateTime)
    
    # Relationships
    requester = db.relationship("User", foreign_keys=[requested_by], backref="requests_made")
    approver = db.relationship("User", foreign_keys=[approved_by], backref="requests_approved")


# =======================
# AUDIT TRAIL
# =======================
class AuditTrail(db.Model):
    """Enhanced audit trail"""
    __tablename__ = "audit_trail"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=True)
    action = db.Column(db.String(100), nullable=False)
    module = db.Column(db.String(100), nullable=False, default="GENERAL")
    
    # Enhanced tracking
    action_type = db.Column(db.String(20), default="Normal")
    old_value = db.Column(db.Text)
    new_value = db.Column(db.Text)
    
    details = db.Column(db.Text, nullable=True)
    ip_address = db.Column(db.String(45), nullable=True)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    # Relationship
    user = db.relationship("User", backref="audit_logs", lazy=True)


# =======================
# ANOMALY
# =======================
class Anomaly(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employee.id'))
    payroll_id = db.Column(db.Integer, db.ForeignKey('payroll.id'))
    
    anomaly_type = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String(255), nullable=False)
    severity = db.Column(db.String(50), default="Low")
    
    # Resolution tracking
    resolved = db.Column(db.Boolean, default=False)
    resolved_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    resolved_at = db.Column(db.DateTime)
    resolution_notes = db.Column(db.Text)
    
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)


# =======================
# SECURITY EVENTS
# =======================
class SecurityEvent(db.Model):
    """Logs security-related events"""
    __tablename__ = "security_event"
    
    id = db.Column(db.Integer, primary_key=True)
    event_type = db.Column(db.String(50), nullable=False)
    username = db.Column(db.String(80))
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.String(255))
    details = db.Column(db.Text)
    severity = db.Column(db.String(20), default="Low")
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)


# =======================
# SEPARATION OF DUTIES LOG
# =======================
class SeparationOfDutiesLog(db.Model):
    """Tracks separation of duties checks"""
    __tablename__ = "sod_log"
    
    id = db.Column(db.Integer, primary_key=True)
    rule_name = db.Column(db.String(100), nullable=False)
    action_attempted = db.Column(db.String(100))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    
    status = db.Column(db.String(20))
    details = db.Column(db.Text)
    
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship
    user = db.relationship("User", backref="sod_logs")


# =======================
# 🆕 OPTIONAL: NOTIFICATION MODEL (for future use)
# =======================
class Notification(db.Model):
    """User notifications"""
    __tablename__ = "notification"
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    # Notification content
    type = db.Column(db.String(50))  # approval, info, reminder, alert, success, warning
    title = db.Column(db.String(200))
    message = db.Column(db.Text)
    icon = db.Column(db.String(10))
    
    # Status
    read = db.Column(db.Boolean, default=False)
    
    # Reference (optional link to related object)
    reference_type = db.Column(db.String(50))  # payroll, leave, attendance
    reference_id = db.Column(db.Integer)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    read_at = db.Column(db.DateTime)
    
    # Relationship
    user = db.relationship("User", backref="notifications")



    # ============================================================================
class UserSettings(db.Model):
    __tablename__ = 'user_settings'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), unique=True, nullable=False)
    
    # Notification Preferences
    email_notifications = db.Column(db.Boolean, default=True)
    push_notifications = db.Column(db.Boolean, default=True)
    sms_notifications = db.Column(db.Boolean, default=False)
    
    # Notification Types
    leave_requests = db.Column(db.Boolean, default=True)
    payroll_alerts = db.Column(db.Boolean, default=True)
    attendance_reminders = db.Column(db.Boolean, default=True)
    
    # Security Settings
    two_factor_auth = db.Column(db.Boolean, default=False)
    session_timeout = db.Column(db.Integer, default=30)
    
    # Display Preferences
    theme = db.Column(db.String(20), default='light')
    language = db.Column(db.String(10), default='en')
    date_format = db.Column(db.String(20), default='MM/DD/YYYY')
    time_format = db.Column(db.String(10), default='12h')
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref=db.backref('settings', uselist=False))
    
    def to_dict(self):
        return {
            'emailNotifications': self.email_notifications,
            'pushNotifications': self.push_notifications,
            'smsNotifications': self.sms_notifications,
            'leaveRequests': self.leave_requests,
            'payrollAlerts': self.payroll_alerts,
            'attendanceReminders': self.attendance_reminders,
            'twoFactorAuth': self.two_factor_auth,
            'sessionTimeout': str(self.session_timeout),
            'theme': self.theme,
            'language': self.language,
            'dateFormat': self.date_format,
            'timeFormat': self.time_format
        }
