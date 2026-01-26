# Fix for leave-requests endpoint
with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Find and replace the stub endpoint
old_code = '''@app.route("/leave-requests", methods=["GET"])
@jwt_required()
def get_leave_requests():
    """Get all leave requests (Admin/HR can see all, Employee sees only their own)"""
    current_user = get_jwt_identity()
    user = User.query.filter_by(username=current_user).first()
    return jsonify([]), 200'''

new_code = '''@app.route("/leave-requests", methods=["GET"])
@jwt_required()
def get_leave_requests():
    """Get all leave requests (Admin/HR can see all, Employee sees only their own)"""
    current_user = get_jwt_identity()
    user = User.query.filter_by(username=current_user).first()
    
    if not user:
        return jsonify({"msg": "User not found"}), 404
    
    # Admin and HR see all leave requests
    if user.role in ['Admin', 'HR Officer', 'Department Manager']:
        leaves = LeaveRequest.query.all()
    else:
        # Employees only see their own
        employee = Employee.query.filter_by(user_id=user.id).first()
        if not employee:
            return jsonify([]), 200
        leaves = LeaveRequest.query.filter_by(employee_id=employee.id).all()
    
    # Format response with employee names
    result = []
    for leave in leaves:
        employee = Employee.query.get(leave.employee_id)
        result.append({
            'id': leave.id,
            'employee_id': leave.employee_id,
            'employee_name': employee.name if employee else 'Unknown',
            'start_date': leave.start_date.strftime('%Y-%m-%d'),
            'end_date': leave.end_date.strftime('%Y-%m-%d'),
            'leave_type': leave.leave_type,
            'reason': leave.reason,
            'days_requested': leave.days_requested,
            'status': leave.status,
            'requested_at': leave.requested_at.strftime('%Y-%m-%d %H:%M:%S'),
            'approved_at': leave.approved_at.strftime('%Y-%m-%d %H:%M:%S') if leave.approved_at else None,
            'rejection_reason': leave.rejection_reason
        })
    
    return jsonify(result), 200'''

content = content.replace(old_code, new_code)

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(content)

print('✅ Leave requests endpoint implemented!')
