from flask import Blueprint, request, jsonify, current_app
from utils.auth import jwt_required 

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['POST'])
def login():
    """
    Inicia sesión de un cliente y retorna un JWT.
    Body: {"email": "cliente@example.com", "password": "secure_password"}
    """
    data = request.json
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({"error": "Email and password are required"}), 400

    token, error = current_app.auth_service.login_customer(email, password)
    if error:
        return jsonify({"error": error}), 401
    
    return jsonify({"message": "Login successful", "access_token": token}), 200

@auth_bp.route('/register_customer', methods=['POST'])
def register_customer():
    """
    Registra un nuevo cliente con nombre, email y contraseña.
    Body: {"name": "Nombre Cliente", "email": "cliente@example.com", "password": "secure_password"}
    """
    data = request.json
    name = data.get('name')
    email = data.get('email')
    password = data.get('password') 

    if not name or not email or not password:
        return jsonify({"error": "Name, email, and password are required"}), 400

    customer_id, error = current_app.auth_service.register_customer(name, email, password) 
    if error:
        return jsonify({"error": error}), 409 
    
    return jsonify({
        "message": "Customer registered successfully",
        "customer_id": customer_id
    }), 201
