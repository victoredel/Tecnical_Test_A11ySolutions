from flask import Blueprint, request, jsonify, current_app
from utils.auth import jwt_required 
from datetime import datetime, timedelta

metrics_bp = Blueprint('metrics', __name__, url_prefix='/metrics')

@metrics_bp.route('/mrr', methods=['GET'])
@jwt_required
def get_mrr(current_user_id):
    """
    Retorna el Ingreso Recurrente Mensual (MRR) actual.
    """
    mrr = current_app.metrics_service.calculate_mrr()
    return jsonify({"mrr": mrr}), 200

@metrics_bp.route('/arr', methods=['GET'])
@jwt_required
def get_arr(current_user_id):
    """
    Retorna el Ingreso Recurrente Anual (ARR) actual.
    """
    arr = current_app.metrics_service.calculate_arr()
    return jsonify({"arr": arr}), 200

@metrics_bp.route('/arpu', methods=['GET'])
@jwt_required
def get_arpu(current_user_id):
    """
    Retorna el Ingreso Medio por Usuario (ARPU) actual.
    """
    arpu = current_app.metrics_service.calculate_arpu()
    return jsonify({"arpu": arpu}), 200

@metrics_bp.route('/retention', methods=['GET'])
@jwt_required
def get_retention_rate(current_user_id):
    """
    Retorna la Tasa de Retención de Clientes (CRR) para un período dado.
    Parámetros de consulta: start_date, end_date (formato: YYYY-MM-DD)
    """
    start_date_str = request.args.get('start_date')
    end_date_str = request.args.get('end_date')

    if not start_date_str or not end_date_str:
        return jsonify({"error": "start_date and end_date are required query parameters"}), 400

    try:
        start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
        end_date = datetime.strptime(end_date_str, "%Y-%m-%d") + timedelta(days=1, seconds=-1) 
    except ValueError:
        return jsonify({"error": "Invalid date format. Use YYYY-MM-DD"}), 400

    if start_date >= end_date:
        return jsonify({"error": "start_date must be before end_date"}), 400

    retention_rate = current_app.metrics_service.calculate_customer_retention_rate(start_date, end_date)
    return jsonify({"customer_retention_rate": retention_rate}), 200

@metrics_bp.route('/churn', methods=['GET'])
@jwt_required
def get_churn_rate(current_user_id):
    """
    Retorna la Tasa de Abandono (Churn Rate - CR) para un período dado.
    Parámetros de consulta: start_date, end_date (formato: YYYY-MM-DD)
    """
    start_date_str = request.args.get('start_date')
    end_date_str = request.args.get('end_date')

    if not start_date_str or not end_date_str:
        return jsonify({"error": "start_date and end_date are required query parameters"}), 400

    try:
        start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
        end_date = datetime.strptime(end_date_str, "%Y-%m-%d") + timedelta(days=1, seconds=-1)
    except ValueError:
        return jsonify({"error": "Invalid date format. Use YYYY-MM-DD"}), 400

    if start_date >= end_date:
        return jsonify({"error": "start_date must be before end_date"}), 400

    churn_rate = current_app.metrics_service.calculate_churn_rate(start_date, end_date)
    return jsonify({"churn_rate": churn_rate}), 200

@metrics_bp.route('/aov', methods=['GET'])
@jwt_required
def get_aov(current_user_id):
    """
    Retorna el Valor Promedio del Pedido (AOV).
    """
    aov = current_app.metrics_service.calculate_aov()
    return jsonify({"average_order_value": aov}), 200

@metrics_bp.route('/rpr', methods=['GET'])
@jwt_required
def get_rpr(current_user_id):
    """
    Retorna la Tasa de Compra Repetida (RPR).
    """
    rpr = current_app.metrics_service.calculate_rpr()
    return jsonify({"repeat_purchase_rate": rpr}), 200

@metrics_bp.route('/purchase_frequency', methods=['GET'])
@jwt_required
def get_purchase_frequency(current_user_id):
    """
    Retorna la frecuencia de compra promedio (suscripciones por cliente).
    """
    frequency = current_app.metrics_service.calculate_purchase_frequency()
    return jsonify({"purchase_frequency": frequency}), 200
