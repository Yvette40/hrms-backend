import os
import secrets
import logging
from datetime import datetime, timedelta
from logging.handlers import RotatingFileHandler

from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

# Internal Imports (Ensure these files exist)
from database import db
from models import User, Employee, Attendance
from validators import (
    validate_email, validate_password, validate_national_id,
    validate_phone, validate_username, validate_salary,
    sanitize_string, validate_required_fields
)

app = Flask(__name__)

# ============================================================================
# 1. CONFIGURATION & SECURITY
# ============================================================================
app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY", secrets.token_hex(32))
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", secrets.token_hex(32))
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///hrms.db" # Adjust to your DB
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Cookie Security
app.config['SESSION_COOKIE_SECURE'] = True
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

db.init_app(app)
jwt = JWTManager(app)

# Initialize Rate Limiter
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://"
)

# CORS Configuration
allowed_origins = os.getenv('CORS_ORIGINS', 'http://localhost:3000').split(',')
CORS(app, resources={
    r"/*": {
        "origins": allowed_origins,
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"],
        "supports_credentials": True
    }
})

# ============================================================================
# 2. LOGGING & AUDIT
# ============================================================================
if not app.debug:
    os.makedirs('logs', exist_ok=True)
    file_handler = RotatingFileHandler('logs/hrms.log', maxBytes=10240000, backupCount=10)
    file_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s: %(message)s'))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)

def log_audit_action_safe(db_session, action_type, description, module, user_id=None, ip_address=None):
    """Helper to log actions to console/file (Add Audit model logic here if needed)"""
    app.logger.info(f"AUDIT: [{module}] {action_type} - {description} (User: {user_id}, IP: {ip_address})")

# ============================================================================
# 3. AUTHENTICATION ENDPOINTS
# ============================================================================

@app.route("/login", methods=["POST"])
@limiter.limit("5 per minute")
def login():
    data = request.json
    if not data or not data.get("username") or not data.get("password"):
        return jsonify({"msg": "Username and password are required"}), 400
    
    username = sanitize_string(data["username"])
    user = User.query.filter_by(username=username).first()
    
    if not user or not user.check_password(data["password"]):
        log_audit_action_safe(db, "LOGIN_FAILED", f"Failed login: {username}", "AUTH", ip_address=request.remote_addr)
        return jsonify({"msg": "Invalid credentials"}), 401

    if not user.is_active:
        return jsonify({"msg": "Account is inactive"}), 403

    user.last_login = datetime.utcnow()
    db.session.commit()

    # Access Token
    expires = timedelta(hours=int(os.getenv('JWT_ACCESS_TOKEN_EXPIRES', 24)))
    access_token = create_access_token(identity=user.username, expires_delta=expires)
    
    # Linked Profile Logic
    emp = user.employee_profile # Assumes relationship 'employee_profile' in User model
    
    resp = {
        'access_token': access_token,
        'role': user.role,
        'username': user.username,
        'employee_id': emp.id if emp else None,
        'employee_name': emp.name if emp else user.username
    }
    return jsonify(resp), 200

# ============================================================================
# 4. EMPLOYEE MANAGEMENT
# ============================================================================

@app.route("/employees", methods=["POST"])
@jwt_required()
def create_employee():
    current_identity = get_jwt_identity()
    creator = User.query.filter_by(username=current_identity).first()
    data = request.json
    
    # Validation
    is_valid, msg = validate_required_fields(data, ['name', 'national_id', 'base_salary'])
    if not is_valid: return jsonify({"msg": msg}), 400
    
    try:
        new_emp = Employee(
            name=sanitize_string(data['name']),
            national_id=data['national_id'],
            base_salary=float(data['base_salary']),
            department=sanitize_string(data.get('department', 'General')),
            created_by=creator.id
        )
        db.session.add(new_emp)
        db.session.commit()
        return jsonify({"msg": "Employee created", "id": new_emp.id}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"msg": str(e)}), 500

# ============================================================================
# 5. MIDDLEWARE & HEALTH
# ============================================================================

@app.after_request
def set_security_headers(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    return response

@app.route('/health', methods=['GET'])
def health_check():
    try:
        db.session.execute(db.text('SELECT 1'))
        return jsonify({"status": "healthy", "database": "connected"}), 200
    except Exception as e:
        return jsonify({"status": "unhealthy", "error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)