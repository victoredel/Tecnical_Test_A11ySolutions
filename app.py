from flask import Flask
from services.auth_service import AuthService
from services.subscription_service import SubscriptionService
from services.metrics_service import MetricsService
from database import init_db, get_db

from routes.auth_routes import auth_bp
from routes.subscription_routes import subscription_bp
from routes.metrics_routes import metrics_bp

def create_app():
    """
    Crea, configura y retorna una instancia de la aplicación Flask.
    Esta función es utilizada tanto para la ejecución principal de la aplicación como para pruebas.
    """
    app = Flask(__name__)

    init_db()
    db_instance = get_db()

    app.auth_service = AuthService(db_instance)
    app.subscription_service = SubscriptionService(db_instance)
    app.metrics_service = MetricsService(db_instance)

    app.register_blueprint(auth_bp)
    app.register_blueprint(subscription_bp)
    app.register_blueprint(metrics_bp) 

    return app 

if __name__ == '__main__':
    app_instance = create_app()
    app_instance.run(debug=True, host='0.0.0.0', port=5000)
