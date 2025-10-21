from functools import wraps
from flask_jwt_extended import get_jwt_identity
from app.models.user import User

def role_required(allowed_roles):
    """
    Decorator to check if user has required role
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            user_id = get_jwt_identity()
            user = User.query.get(user_id)
            
            if not user or not user.is_active:
                return {'message': 'User not found or inactive'}, 401
            
            if user.role not in allowed_roles:
                return {'message': 'Insufficient permissions'}, 403
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator