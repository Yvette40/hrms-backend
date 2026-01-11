# =====================================================
# USER MANAGEMENT ENDPOINTS - ADD THIS TO YOUR app.py
# =====================================================

@app.route("/register", methods=["POST"])
def register():
    """Register a new user (Admin only)"""
    data = request.json
    
    if not data.get("username") or not data.get("password"):
        return jsonify({"msg": "Username and password are required"}), 400
    
    # Check if username already exists
    if User.query.filter_by(username=data["username"]).first():
        return jsonify({"msg": "Username already exists"}), 400
    
    # Create new user
    new_user = User(
        username=data["username"],
        role=data.get("role", "Employee")  # Default to Employee role
    )
    new_user.set_password(data["password"])
    
    db.session.add(new_user)
    db.session.commit()
    
    log_audit_action_safe(
        db,
        action_type="USER_CREATED",
        description=f"New user created: {data['username']} with role {new_user.role}",
        module="USER_MANAGEMENT",
        ip_address=request.remote_addr,
    )
    
    return jsonify({
        "msg": "User created successfully",
        "user": {
            "id": new_user.id,
            "username": new_user.username,
            "role": new_user.role
        }
    }), 201


@app.route("/users", methods=["GET"])
@jwt_required()
def get_users():
    """Get all users (Admin only)"""
    current_user = get_jwt_identity()
    user = User.query.filter_by(username=current_user).first()
    
    # Check if user is admin
    if user.role != "Admin":
        return jsonify({"msg": "Admin access required"}), 403
    
    users = User.query.all()
    
    result = [
        {
            "id": u.id,
            "username": u.username,
            "role": u.role,
            "created_at": u.created_at.strftime("%Y-%m-%d %H:%M:%S") if hasattr(u, 'created_at') else None
        }
        for u in users
    ]
    
    return jsonify(result), 200


@app.route("/users/<int:user_id>", methods=["DELETE"])
@jwt_required()
def delete_user(user_id):
    """Delete a user (Admin only)"""
    current_user = get_jwt_identity()
    user = User.query.filter_by(username=current_user).first()
    
    # Check if user is admin
    if user.role != "Admin":
        return jsonify({"msg": "Admin access required"}), 403
    
    # Prevent deleting yourself
    if user.id == user_id:
        return jsonify({"msg": "Cannot delete your own account"}), 400
    
    user_to_delete = User.query.get_or_404(user_id)
    username = user_to_delete.username
    
    db.session.delete(user_to_delete)
    db.session.commit()
    
    log_audit_action_safe(
        db,
        action_type="USER_DELETED",
        description=f"Deleted user: {username}",
        module="USER_MANAGEMENT",
        user_id=user.id,
        ip_address=request.remote_addr,
    )
    
    return jsonify({"msg": f"User {username} deleted successfully"}), 200
