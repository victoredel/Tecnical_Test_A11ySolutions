from services.auth_service import AuthService
from utils.security import hash_password, verify_password
from bson import ObjectId
from datetime import datetime, timedelta, timezone
import jwt
from config import Config

Config.JWT_SECRET_KEY = "test_secret_key"
Config.JWT_ACCESS_TOKEN_EXPIRES_SECONDS = 3600

def test_register_customer_success(mock_db):
    """
    Verifica que un cliente se registra exitosamente.
    """
    mock_db['customers'].find_one.return_value = None
    mock_db['customers'].insert_one.return_value.inserted_id = ObjectId()

    auth_service = AuthService(mock_db['db'])
    customer_id, error = auth_service.register_customer("Test User", "test@example.com", "password123")

    assert error is None
    assert isinstance(customer_id, str)
    mock_db['customers'].insert_one.assert_called_once()
    assert mock_db['customers'].insert_one.call_args[0][0]['email'] == "test@example.com"
    assert 'password_hash' in mock_db['customers'].insert_one.call_args[0][0]

def test_register_customer_email_exists(mock_db):
    """
    Verifica que el registro falla si el email ya existe.
    """
    mock_db['customers'].find_one.return_value = {"email": "existing@example.com"}

    auth_service = AuthService(mock_db['db'])
    customer_id, error = auth_service.register_customer("Existing User", "existing@example.com", "password123")

    assert customer_id is None
    assert "already exists" in error
    mock_db['customers'].insert_one.assert_not_called()

def test_login_customer_success(mock_db, mocker):
    """
    Verifica que el login es exitoso y devuelve un JWT válido.
    """
    hashed_pwd = hash_password("password123")
    mock_db['customers'].find_one.return_value = {
        "_id": ObjectId("60d5ec49f7e3b1a2b3c4d5e6"),
        "email": "login@example.com",
        "password_hash": hashed_pwd
    }
    
    mocker.patch('time.time', return_value=datetime.utcnow().timestamp())
    auth_service = AuthService(mock_db['db'])
    token, error = auth_service.login_customer("login@example.com", "password123")

    assert error is None
    assert isinstance(token, str)

    decoded_payload = jwt.decode(token, Config.JWT_SECRET_KEY, algorithms=["HS256"])
    assert decoded_payload["sub"] == "60d5ec49f7e3b1a2b3c4d5e6"
    assert decoded_payload["email"] == "login@example.com"

def test_login_customer_invalid_credentials_email(mock_db):
    """
    Verifica que el login falla con credenciales inválidas (email no encontrado).
    """
    mock_db['customers'].find_one.return_value = None 

    auth_service = AuthService(mock_db['db'])
    token, error = auth_service.login_customer("nonexistent@example.com", "password123")

    assert token is None
    assert "Invalid credentials" in error

def test_login_customer_invalid_credentials_password(mock_db):
    """
    Verifica que el login falla con credenciales inválidas (contraseña incorrecta).
    """
    hashed_pwd = hash_password("correctpassword")
    mock_db['customers'].find_one.return_value = {
        "_id": ObjectId(),
        "email": "login@example.com",
        "password_hash": hashed_pwd
    }

    auth_service = AuthService(mock_db['db'])
    token, error = auth_service.login_customer("login@example.com", "wrongpassword")

    assert token is None
    assert "Invalid credentials" in error

def test_get_customer_by_id_success(mock_db):
    """
    Verifica que se puede obtener un cliente por su ID.
    """
    customer_id = ObjectId("60d5ec49f7e3b1a2b3c4d5e6")
    mock_db['customers'].find_one.return_value = {"_id": customer_id, "email": "test@example.com"}

    auth_service = AuthService(mock_db['db'])
    customer = auth_service.get_customer_by_id(str(customer_id))

    assert customer is not None
    assert str(customer["_id"]) == str(customer_id)

def test_get_customer_by_id_invalid_id(mock_db):
    """
    Verifica que devuelve None para un ID inválido.
    """
    auth_service = AuthService(mock_db['db'])
    customer = auth_service.get_customer_by_id("invalid_id_format")

    assert customer is None
    mock_db['customers'].find_one.assert_not_called() # No debería intentar buscar en la DB
