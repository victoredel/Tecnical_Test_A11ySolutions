from flask import Flask, request, jsonify
from services.auth_service import AuthService
from services.subscription_service import SubscriptionService 
from database import init_db
from utils.auth import jwt_required 

app = Flask(__name__)
init_db()
auth_service = AuthService()
subscription_service = SubscriptionService()

@app.route('/login', methods=['POST'])
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

    token, error = auth_service.login_customer(email, password)
    if error:
        return jsonify({"error": error}), 401
    
    return jsonify({"message": "Login successful", "access_token": token}), 200

@app.route('/register_customer', methods=['POST'])
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

    customer_id, error = auth_service.register_customer(name, email, password) 
    if error:
        return jsonify({"error": error}), 409 
    
    return jsonify({
        "message": "Customer registered successfully",
        "customer_id": customer_id
    }), 201


@app.route('/add_product', methods=['POST'])
@jwt_required
def add_product(current_user_id):
    """
    Añade un nuevo producto.
    Body: {"name": "Nombre Producto", "description": "Descripción", "customizable": true/false}
    """
    data = request.json
    name = data.get('name')
    description = data.get('description')
    customizable = data.get('customizable', False) 

    if not name or not description:
        return jsonify({"error": "Name and description are required"}), 400
    
    product_id, error = subscription_service.add_product(name, description, customizable)
    if error:
        return jsonify({"error": error}), 409 

    return jsonify({
        "message": "Product added successfully",
        "product_id": product_id
    }), 201

@app.route('/subscribe', methods=['POST'])
@jwt_required
def subscribe(current_user_id):
    """
    Permite a un cliente suscribirse a un producto.
    Body: {"customer_id": "...", "product_id": "...", "expiration_date": "YYYY-MM-DDTHH:MM:SS", "customization": {...}}
    """
    data = request.json
    customer_id_str = data.get('customer_id')
    product_id_str = data.get('product_id')
    expiration_date_str = data.get('expiration_date')
    customization = data.get('customization')

    if not all([customer_id_str, product_id_str, expiration_date_str]):
        return jsonify({"error": "customer_id, product_id, and expiration_date are required"}), 400

    if customer_id_str != current_user_id:
        return jsonify({"error": "You can only subscribe on behalf of yourself."}), 403

    subscription_id, error = subscription_service.subscribe_customer_to_product(
        customer_id_str, product_id_str, expiration_date_str, customization
    )

    if error:
        if "Invalid" in error or "Use ISO format" in error:
            return jsonify({"error": error}), 400
        elif "not found" in error:
            return jsonify({"error": error}), 404
        elif "already has an active subscription" in error or "Product is not customizable" in error:
            return jsonify({"error": error}), 409
        return jsonify({"error": error}), 500 
    
    return jsonify({
        "message": "Subscription created successfully",
        "subscription_id": subscription_id
    }), 201

@app.route('/subscription_status/<string:subscription_id_str>', methods=['GET'])
@jwt_required 
def get_subscription_status(subscription_id_str, current_user_id):
    """
    Retorna si la suscripción está activa o expirada.
    """
    
    subscription = subscription_service.get_subscription_by_id(subscription_id_str)
    if subscription and str(subscription["customer_id"]) != current_user_id:
       return jsonify({"error": "You are not authorized to view this subscription's status"}), 403

    status, error = subscription_service.get_subscription_status(subscription_id_str)
    if error:
        if "Invalid" in error:
            return jsonify({"error": error}), 400
        return jsonify({"error": error}), 404
    return jsonify({"subscription_id": subscription_id_str, "status": status}), 200

@app.route('/subscription_settings/<string:subscription_id_str>', methods=['GET'])
@jwt_required
def get_subscription_settings(subscription_id_str, current_user_id):
    """
    Retorna la configuración específica de una suscripción.
    """
    
    subscription = subscription_service.get_subscription_by_id(subscription_id_str)
    if subscription and str(subscription["customer_id"]) != current_user_id:
       return jsonify({"error": "You are not authorized to view these settings"}), 403

    settings, error = subscription_service.get_subscription_settings(subscription_id_str)
    if error:
        if "Invalid" in error:
            return jsonify({"error": error}), 400
        elif "not found" in error:
            return jsonify({"error": error}), 404
        elif "Product associated with this subscription is not customizable" in error:
            return jsonify({"error": error}), 400 
        return jsonify({"error": error}), 500 
    return jsonify({
        "subscription_id": subscription_id_str,
        "settings": settings
    }), 200

@app.route('/edit_subscription_settings/<string:subscription_id_str>', methods=['PUT'])
@jwt_required
def edit_subscription_settings(subscription_id_str, current_user_id):
    """
    Modifica la configuración específica de una suscripción.
    Body: {"settings": {"new_key": "new_value"}}
    """
    
    subscription = subscription_service.get_subscription_by_id(subscription_id_str)
    if subscription and str(subscription["customer_id"]) != current_user_id:
       return jsonify({"error": "You are not authorized to edit these settings"}), 403

    data = request.json
    new_settings = data.get('settings')

    if not new_settings:
        return jsonify({"error": "New settings are required"}), 400

    success, error = subscription_service.edit_subscription_settings(subscription_id_str, new_settings)
    if error:
        if "Invalid" in error:
            return jsonify({"error": error}), 400
        elif "not found" in error:
            return jsonify({"error": error}), 404
        elif "Product associated with this subscription is not customizable" in error:
            return jsonify({"error": error}), 400
        elif "Settings already up to date" in error:
            return jsonify({"message": error}), 200 
        return jsonify({"error": error}), 500
    
    if success:
        return jsonify({"message": "Subscription settings updated successfully"}), 200
    return jsonify({"error": "Failed to update subscription settings"}), 500

@app.route('/extend_subscription/<string:subscription_id_str>', methods=['PUT'])
@jwt_required
def extend_subscription(subscription_id_str, current_user_id):
    """
    Establece una nueva fecha de expiración para una suscripción.
    Body: {"new_expiration_date": "YYYY-MM-DDTHH:MM:SS"}
    """
    
    subscription = subscription_service.get_subscription_by_id(subscription_id_str)
    if subscription and str(subscription["customer_id"]) != current_user_id:
       return jsonify({"error": "You are not authorized to extend this subscription"}), 403

    data = request.json
    new_expiration_date_str = data.get('new_expiration_date')

    if not new_expiration_date_str:
        return jsonify({"error": "New expiration date is required"}), 400

    success, error = subscription_service.extend_subscription(subscription_id_str, new_expiration_date_str)
    if error:
        if "Invalid" in error:
            return jsonify({"error": error}), 400
        elif "not found" in error:
            return jsonify({"error": error}), 404
        elif "Subscription expiration date already set to this value" in error:
            return jsonify({"message": error}), 200 
        return jsonify({"error": error}), 500
    
    if success:
        return jsonify({"message": "Subscription extended successfully"}), 200
    return jsonify({"error": "Failed to extend subscription"}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)