import jwt
from flask import request, jsonify
from functools import wraps
from config import Config
from services.auth_service import AuthService 

auth_service = AuthService() 

def jwt_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization')

        if not auth_header:
            return jsonify({"error": "Authorization header is missing"}), 401 # No autorizado
        
        try:
            token_type, token = auth_header.split(None, 1) # Divide "Bearer <token>"
        except ValueError:
            return jsonify({"error": "Invalid Authorization header format"}), 401
        
        if token_type.lower() != 'bearer':
            return jsonify({"error": "Unsupported authorization type"}), 401

        try:
            payload = jwt.decode(token, Config.JWT_SECRET_KEY, algorithms=["HS256"])
            
            user_id = payload.get('sub')
            if not user_id or not auth_service.get_customer_by_id(user_id):
                return jsonify({"error": "User specified in token not found"}), 401

            kwargs['current_user_id'] = user_id 

        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token has expired"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"error": "Invalid token"}), 401
        except Exception as e:
            return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500
        
        return f(*args, **kwargs)
    return decorated_function