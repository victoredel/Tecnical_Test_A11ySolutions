from flask import Blueprint, request, jsonify, current_app
from utils.auth import jwt_required 
from datetime import datetime, timedelta

subscription_bp = Blueprint('subscription', __name__)

@subscription_bp.route('/add_product', methods=['POST'])
@jwt_required
def add_product(current_user_id):
    """
    Añade un nuevo producto.
    Body: {"name": "Nombre Producto", "description": "Descripción", "customizable": true/false, "price": 100.0, "periodicity": "monthly"}
    """
    data = request.json
    name = data.get('name')
    description = data.get('description')
    customizable = data.get('customizable', False)
    price = data.get('price')           
    periodicity = data.get('periodicity') 

    if not all([name, description, price, periodicity]): 
        return jsonify({"error": "Name, description, price, and periodicity are required"}), 400
    
    product_id, error = current_app.subscription_service.add_product(name, description, customizable, price, periodicity)
    if error:
        return jsonify({"error": error}), 409

    return jsonify({
        "message": "Product added successfully",
        "product_id": product_id
    }), 201

@subscription_bp.route('/subscribe', methods=['POST'])
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

    subscription_id, error = current_app.subscription_service.subscribe_customer_to_product(
        customer_id_str, product_id_str, expiration_date_str, customization
    )

    if error:
        if "Invalid" in error or "Use ISO format" in error:
            return jsonify({"error": error}), 400
        elif "not found" in error:
            return jsonify({"error": error}), 404
        elif "already has an active subscription" in error or "Product is not customizable" in error or "Product is missing price or periodicity data" in error or "Expiration date cannot be in the past" in error:
            return jsonify({"error": error}), 409
        return jsonify({"error": error}), 500 
    
    return jsonify({
        "message": "Subscription created successfully",
        "subscription_id": subscription_id
    }), 201

@subscription_bp.route('/subscription_status/<string:subscription_id_str>', methods=['GET'])
@jwt_required 
def get_subscription_status(subscription_id_str, current_user_id):
    subscription = current_app.subscription_service.get_subscription_by_id(subscription_id_str)
    if not subscription:
        return jsonify({"error": "Subscription not found"}), 404

    if str(subscription["customer_id"]) != current_user_id:
       return jsonify({"error": "You are not authorized to view this subscription's status"}), 403

    status, error = current_app.subscription_service.get_subscription_status(subscription_id_str)
    if error:
        if "Invalid" in error:
            return jsonify({"error": error}), 400
        return jsonify({"error": error}), 404
    return jsonify({"subscription_id": subscription_id_str, "status": status}), 200

@subscription_bp.route('/subscription_settings/<string:subscription_id_str>', methods=['GET'])
@jwt_required
def get_subscription_settings(subscription_id_str, current_user_id):
    subscription = current_app.subscription_service.get_subscription_by_id(subscription_id_str)
    if not subscription:
        return jsonify({"error": "Subscription not found"}), 404

    if str(subscription["customer_id"]) != current_user_id:
       return jsonify({"error": "You are not authorized to view these settings"}), 403

    settings, error = current_app.subscription_service.get_subscription_settings(subscription_id_str)
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

@subscription_bp.route('/edit_subscription_settings/<string:subscription_id_str>', methods=['PUT'])
@jwt_required
def edit_subscription_settings(subscription_id_str, current_user_id):
    subscription = current_app.subscription_service.get_subscription_by_id(subscription_id_str)
    if not subscription:
        return jsonify({"error": "Subscription not found"}), 404

    if str(subscription["customer_id"]) != current_user_id:
       return jsonify({"error": "You are not authorized to edit these settings"}), 403

    data = request.json
    new_settings = data.get('settings')

    if not new_settings:
        return jsonify({"error": "New settings are required"}), 400

    success, error = current_app.subscription_service.edit_subscription_settings(subscription_id_str, new_settings)
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

@subscription_bp.route('/extend_subscription/<string:subscription_id_str>', methods=['PUT'])
@jwt_required
def extend_subscription(subscription_id_str, current_user_id):
    """
    Establece una nueva fecha de expiración para una suscripción.
    Body: {"new_expiration_date": "YYYY-MM-DDTHH:MM:SS"}
    """
    subscription = current_app.subscription_service.get_subscription_by_id(subscription_id_str)
    if not subscription:
        return jsonify({"error": "Subscription not found"}), 404

    if str(subscription["customer_id"]) != current_user_id:
       return jsonify({"error": "You are not authorized to extend this subscription"}), 403

    data = request.json
    new_expiration_date_str = data.get('new_expiration_date')

    if not new_expiration_date_str:
        return jsonify({"error": "New expiration date is required"}), 400

    success, error = current_app.subscription_service.extend_subscription(subscription_id_str, new_expiration_date_str)
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
