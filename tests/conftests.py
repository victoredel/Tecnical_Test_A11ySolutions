import pytest
from app import app as flask_app
from database import get_db, init_db 
from pymongo import MongoClient

@pytest.fixture
def client():
    """
    Configura la aplicación Flask para pruebas.
    Usa un cliente de prueba para hacer solicitudes HTTP.
    """
    flask_app.config['TESTING'] = True
    with flask_app.test_client() as client:
        yield client 

@pytest.fixture(autouse=True)
def mock_db(mocker):
    """
    Mocks la conexión a MongoDB para que los tests no interactúen con una DB real.
    """
    mock_client = mocker.Mock(spec=MongoClient)
    mock_db_instance = mocker.Mock()
    
    mock_client.__getitem__.return_value = mock_db_instance
    
    mock_customers_collection = mocker.Mock()
    mock_products_collection = mocker.Mock()
    mock_subscriptions_collection = mocker.Mock()

    mock_db_instance.customers = mock_customers_collection
    mock_db_instance.products = mock_products_collection
    mock_db_instance.subscriptions = mock_subscriptions_collection

    mocker.patch('database.get_db', return_value=mock_db_instance)
    mocker.patch('database.init_db') 
    
    return {
        "db": mock_db_instance,
        "customers": mock_customers_collection,
        "products": mock_products_collection,
        "subscriptions": mock_subscriptions_collection
    }

# Fixture para mockear datetime.utcnow() para pruebas de tiempo
@pytest.fixture
def mock_datetime_utcnow(mocker):
    """
    Mocks datetime.utcnow() para controlar el tiempo en los tests.
    """
    mock_dt = mocker.patch('datetime.datetime')
    mock_dt.utcnow.return_value = datetime(2024, 1, 1, 12, 0, 0)
    return mock_dt