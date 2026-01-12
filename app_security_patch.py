# ============================================================================
# SECURITY IMPROVEMENTS FOR app.py
# ============================================================================
# This file contains the code changes needed to fix security issues
# Copy and paste these sections into your app.py file
# ============================================================================

# ============================================================================
# 1. ADD IMPORTS AT THE TOP (after existing imports)
# ============================================================================

from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import logging
from logging.handlers import RotatingFileHandler
import secrets

# Import validators (create this file using validators.py provided)
from validators import (
    validate_email, validate_password, validate_national_id,
    validate_phone, validate_username, validate_salary,
    sanitize_string, validate_required_fields
)


# ============================================================================
# 2. REPLACE THE CONFIGURATION SECTION (around line 50-65)
# ============================================================================
# OLD CODE (REMOVE):
# app.config["JWT_SECRET_KEY"] = "super-secret-key"

# NEW CODE (USE THIS):
app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY", secrets.token_hex(32))
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", secrets.token_hex(32))

# Add security headers
app.config['SESSION_COOKIE_SECURE'] = True
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'


# ============================================================================
# 3. ADD RATE LIMITER (after app initialization)
# ============================================================================

# Initialize rate limiter
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://"
)


# ============================================================================
# 4. ADD LOGGING CONFIGURATION (after app initialization)
# ============================================================================

# Configure logging
if not app.debug:
    # Create logs directory
    os.makedirs('logs', exist_ok=True)
    
    # File handler with rotation
    file_handler = RotatingFileHandler(
        'logs/hrms.log',
        maxBytes=10240000,  # 10MB
        backupCount=10
    )
    
    # Formatter
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    ))
    
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)
    app.logger.info('HRMS startup')


# ============================================================================
# 5. UPDATE CORS CONFIGURATION (around line 39-47)
# ============================================================================

# Get allowed origins from environment variable
allowed_origins = os.getenv('CORS_ORIGINS', 'http://localhost:3000').split(',')

CORS(app, resources={
    r"/*": {
        "origins": allowed_origins,
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"],
        "supports_credentials": True,
        "expose_headers": ["Content-Type", "Authorization"]
    }
})


# ============================================================================
# 6. REPLACE LOGIN ENDPOINT (around line 326)
# ============================================================================

@app.route("/login", methods=["POST"])
@limiter.limit("5 per minute")  # Add rate limiting
def login():
    data = request.json
    
    # Validate required fields
    if not data or not data.get("username") or not data.get("password"):
        app.logger.warning(f"Login attempt with missing credentials from {request.remote_addr}")
        return jsonify({"msg": "Username and password are required"}), 400
    
    # Sanitize username input
    username = sanitize_string(data["username"])

    user = User.query.filter_by(username=username).first()
    
    if not user or not user.check_password(data["password"]):
        log_audit_action_safe(
            db,
            action_type="LOGIN_FAILED",
            description=f"Failed login attempt for {username}",
            module="AUTH",
            ip_address=request.remote_addr,
        )
        app.logger.warning(f"Failed login attempt for {username} from {request.remote_addr}")
        return jsonify({"msg": "Invalid credentials"}), 401

    # Check if user is active
    if not user.is_active:
        app.logger.warning(f"Login attempt by inactive user {username}")
        return jsonify({"msg": "Account is inactive. Contact administrator."}), 403

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
    
    app.logger.info(f"Successful login for {user.username} from {request.remote_addr}")

    # Create JWT token with expiration
    expires = timedelta(hours=int(os.getenv('JWT_ACCESS_TOKEN_EXPIRES', 24)))
    access_token = create_access_token(identity=user.username, expires_delta=expires)
    
    # Get linked employee profile if exists
    employee_profile = user.employee_profile
    
    # Build response with role and employee data
    response_data = {
        'access_token': access_token,
        'role': user.role,
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
        response_data.update({
            'employee_id': None,
            'employee_national_id': None,
            'employee_name': user.username,
            'department': 'Administration',
            'position': user.role,
            'email': user.email,
            'phone': user.phone,
        })
    
    return jsonify(response_data), 200


# ============================================================================
# 7. UPDATE EMPLOYEE CREATE ENDPOINT (around line 526)
# ============================================================================

@app.route("/employees", methods=["POST"])
@jwt_required()
def create_employee():
    current_user_username = get_jwt_identity()
    current_user = User.query.filter_by(username=current_user_username).first()
    
    data = request.json
    
    # Validate required fields
    required_fields = ['name', 'national_id', 'base_salary']
    is_valid, message = validate_required_fields(data, required_fields)
    if not is_valid:
        return jsonify({"msg": message}), 400
    
    # Validate national ID
    is_valid, message = validate_national_id(data.get('national_id'))
    if not is_valid:
        return jsonify({"msg": message}), 400
    
    # Validate email if provided
    if data.get('email'):
        is_valid, message = validate_email(data.get('email'))
        if not is_valid:
            return jsonify({"msg": message}), 400
    
    # Validate phone if provided
    if data.get('phone_number'):
        is_valid, message = validate_phone(data.get('phone_number'))
        if not is_valid:
            return jsonify({"msg": message}), 400
    
    # Validate salary
    is_valid, message = validate_salary(data.get('base_salary'))
    if not is_valid:
        return jsonify({"msg": message}), 400
    
    # Sanitize string inputs
    name = sanitize_string(data.get('name'))
    department = sanitize_string(data.get('department', 'General'))
    position = sanitize_string(data.get('position', 'Employee'))
    
    # Check if employee already exists
    existing = Employee.query.filter_by(national_id=data['national_id']).first()
    if existing:
        return jsonify({"msg": "Employee with this National ID already exists"}), 400
    
    try:
        employee = Employee(
            name=name,
            national_id=data['national_id'],
            base_salary=float(data['base_salary']),
            department=department,
            position=position,
            email=data.get('email'),
            phone_number=data.get('phone_number'),
            join_date=datetime.strptime(data.get('join_date'), '%Y-%m-%d').date() if data.get('join_date') else datetime.now().date(),
            leave_balance=int(data.get('leave_balance', 21)),
            created_by=current_user.id
        )
        
        db.session.add(employee)
        db.session.commit()
        
        log_audit_action_safe(
            db,
            action_type="EMPLOYEE_CREATE",
            description=f"Created employee: {employee.name} (ID: {employee.national_id})",
            module="EMPLOYEES",
            user_id=current_user.id,
            ip_address=request.remote_addr,
        )
        
        app.logger.info(f"Employee created: {employee.name} by {current_user.username}")
        
        return jsonify({
            "msg": "Employee created successfully",
            "employee": employee.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Error creating employee: {str(e)}")
        return jsonify({"msg": f"Error creating employee: {str(e)}"}), 500


# ============================================================================
# 8. ADD USER CREATION VALIDATION (if you have user creation endpoint)
# ============================================================================

@app.route("/users", methods=["POST"])
@jwt_required()
def create_user():
    current_user_username = get_jwt_identity()
    current_user = User.query.filter_by(username=current_user_username).first()
    
    # Only Admin can create users
    if current_user.role != 'Admin':
        return jsonify({"msg": "Unauthorized"}), 403
    
    data = request.json
    
    # Validate username
    is_valid, message = validate_username(data.get('username'))
    if not is_valid:
        return jsonify({"msg": message}), 400
    
    # Validate password
    is_valid, message = validate_password(data.get('password'))
    if not is_valid:
        return jsonify({"msg": message}), 400
    
    # Validate email if provided
    if data.get('email'):
        is_valid, message = validate_email(data.get('email'))
        if not is_valid:
            return jsonify({"msg": message}), 400
    
    # Check if username exists
    if User.query.filter_by(username=data['username']).first():
        return jsonify({"msg": "Username already exists"}), 400
    
    try:
        user = User(
            username=data['username'],
            role=data.get('role', 'Employee'),
            email=data.get('email'),
            phone=data.get('phone'),
            is_active=True
        )
        user.set_password(data['password'])
        
        db.session.add(user)
        db.session.commit()
        
        log_audit_action_safe(
            db,
            action_type="USER_CREATE",
            description=f"Created user: {user.username} with role {user.role}",
            module="USERS",
            user_id=current_user.id,
            ip_address=request.remote_addr,
        )
        
        app.logger.info(f"User created: {user.username} by {current_user.username}")
        
        return jsonify({
            "msg": "User created successfully",
            "user": {
                "id": user.id,
                "username": user.username,
                "role": user.role,
                "email": user.email
            }
        }), 201
        
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Error creating user: {str(e)}")
        return jsonify({"msg": f"Error creating user: {str(e)}"}), 500


# ============================================================================
# 9. ADD SECURITY HEADERS MIDDLEWARE
# ============================================================================

@app.after_request
def set_security_headers(response):
    """Add security headers to all responses"""
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    
    # Remove server header
    response.headers.pop('Server', None)
    
    return response


# ============================================================================
# 10. ADD HEALTH CHECK ENDPOINT
# ============================================================================

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint for monitoring"""
    try:
        # Check database connection
        db.session.execute('SELECT 1')
        
        return jsonify({
            "status": "healthy",
            "database": "connected",
            "timestamp": datetime.utcnow().isoformat()
        }), 200
        
    except Exception as e:
        app.logger.error(f"Health check failed: {str(e)}")
        return jsonify({
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }), 500


# ============================================================================
# INSTALLATION REQUIREMENTS
# ============================================================================

"""
Add these to requirements.txt:

Flask-Limiter==3.5.0
python-dotenv==1.0.0

Install with:
pip install Flask-Limiter python-dotenv

"""

# ============================================================================
# END OF SECURITY IMPROVEMENTS
# ============================================================================
