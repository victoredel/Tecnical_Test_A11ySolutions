import pytest
from app import create_app
from database import get_db, init_db 
from pymongo import MongoClient

@pytest.fixture
def client():
    """
    Configura la aplicación Flask para pruebas.
    Usa un cliente de prueba para hacer solicitudes HTTP.
    """
    flask_app = create_app()
    flask_app.config['TESTING'] = True
    with flask_app.test_client() as client:
        yield client 

@pytest.fixture(autouse=True)
def mock_db(mocker):
    """
    Mocks la conexión a MongoDB para que los tests no interactúen con una DB real.
    """
    # 1. Mockear la clase MongoClient en sí misma.
    # Esto asegura que cada vez que MongoClient() sea llamado, se devuelva nuestro mock.
    mock_mongo_client_class = mocker.patch('pymongo.MongoClient', autospec=True)
    
    # 2. Crear una instancia mock de MongoClient que será devuelta cuando MongoClient() sea llamado.
    mock_client_instance = mocker.Mock(spec=MongoClient)
    mock_mongo_client_class.return_value = mock_client_instance

    # 3. Crear una instancia mock de la base de datos (lo que get_db() debería devolver).
    mock_db_instance = mocker.Mock()
    
    # 4. Configurar la instancia mock del cliente para que devuelva la base de datos mockeada
    # cuando se acceda con corchetes (ej. client['nombre_db']).
    # Así es como _client[Config.MONGO_DB_NAME] funciona en database.py.
    mock_client_instance.__getitem__ = mocker.Mock(return_value=mock_db_instance)
    
    # 5. Crear mocks para las colecciones individuales (customers, products, subscriptions).
    mock_customers_collection = mocker.Mock()
    mock_products_collection = mocker.Mock()
    mock_subscriptions_collection = mocker.Mock()

    # 6. Configurar la instancia mock de la base de datos para que devuelva los mocks de las colecciones.
    mock_db_instance.customers = mock_customers_collection
    mock_db_instance.products = mock_products_collection
    mock_db_instance.subscriptions = mock_subscriptions_collection

    # 7. Parchear database.init_db y database.get_db.
    # init_db() no hará nada en las pruebas.
    mocker.patch('database.init_db')
    # get_db() devolverá nuestra mock_db_instance.
    mocker.patch('database.get_db', return_value=mock_db_instance)
    
    # Retornar los mocks de las colecciones para que los tests puedan configurar su comportamiento.
    return {
        "db": mock_db_instance,
        "customers": mock_customers_collection,
        "products": mock_products_collection,
        "subscriptions": mock_subscriptions_collection
    }

@pytest.fixture
def mock_datetime_utcnow(mocker):
    """
    Mocks datetime.utcnow() para controlar el tiempo en los tests.
    """
    mock_dt = mocker.patch('datetime.datetime')
    mock_dt.utcnow.return_value = datetime(2024, 1, 1, 12, 0, 0)
    return mock_dt