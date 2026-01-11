from flask import g, request
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity

def load_current_user():
    """
    Middleware function that runs before each request.
    It verifies JWT tokens (if provided) and stores user_id in 'g'.
    """
    g.current_user_id = None  # default to None

    try:
        verify_jwt_in_request(optional=True)
        g.current_user_id = get_jwt_identity()
    except Exception:
        # No valid JWT — continue anonymously
        pass
