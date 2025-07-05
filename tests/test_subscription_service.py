import pytest
from services.subscription_service import SubscriptionService
from bson import ObjectId
from datetime import datetime, timedelta

def test_add_product_success(mock_db):
    """
    Verifica que se puede añadir un producto exitosamente.
    """
    mock_db['products'].find_one.return_value = None
    mock_db['products'].insert_one.return_value.inserted_id = ObjectId()

    subscription_service = SubscriptionService(mock_db['db'])
    product_id, error = subscription_service.add_product(
        "Premium Plan", "Full access to all features", True, 99.99, "monthly"
    )

    assert error is None
    assert isinstance(product_id, str)
    mock_db['products'].insert_one.assert_called_once()
    assert mock_db['products'].insert_one.call_args[0][0]['name'] == "Premium Plan"

def test_add_product_name_exists(mock_db):
    """
    Verifica que no se puede añadir un producto con un nombre ya existente.
    """
    mock_db['products'].find_one.return_value = {"name": "Existing Plan"}

    subscription_service = SubscriptionService(mock_db['db'])
    product_id, error = subscription_service.add_product(
        "Existing Plan", "Description", False, 10.0, "monthly"
    )

    assert product_id is None
    assert "Product with this name already exists" in error
    mock_db['products'].insert_one.assert_not_called()

def test_add_product_invalid_price(mock_db):
    """
    Verifica que no se puede añadir un producto con un precio inválido.
    """    
    mock_db['products'].find_one.return_value = None
    subscription_service = SubscriptionService(mock_db['db'])
    product_id, error = subscription_service.add_product(
        "Invalid Price Plan", "Description", False, -10.0, "monthly"
    )
    assert product_id is None
    assert "Price must be a positive number" in error
    mock_db['products'].insert_one.assert_not_called()

def test_add_product_invalid_periodicity(mock_db):
    """
    Verifica que no se puede añadir un producto con una periodicidad inválida.
    """
    mock_db['products'].find_one.return_value = None
    subscription_service = SubscriptionService(mock_db['db'])
    product_id, error = subscription_service.add_product(
        "Invalid Periodicity Plan", "Description", False, 10.0, "weekly"
    )
    assert product_id is None
    assert "Periodicity must be 'monthly' or 'annually'" in error
    mock_db['products'].insert_one.assert_not_called()

def test_subscribe_customer_to_product_success(mock_db):
    """
    Verifica que un cliente puede suscribirse a un producto exitosamente.
    """
    customer_id = ObjectId()
    product_id = ObjectId()
    
    mock_db['customers'].find_one.return_value = {"_id": customer_id, "email": "test@example.com"}
    mock_db['products'].find_one.return_value = {
        "_id": product_id, "name": "Basic Plan", "price": 10.0, "periodicity": "monthly", "customizable": False
    }
    mock_db['subscriptions'].find_one.return_value = None
    mock_db['subscriptions'].insert_one.return_value.inserted_id = ObjectId()

    subscription_service = SubscriptionService(mock_db['db'])
    expiration_date = (datetime.utcnow() + timedelta(days=30)).isoformat()
    
    subscription_id, error = subscription_service.subscribe_customer_to_product(
        str(customer_id), str(product_id), expiration_date, None
    )

    assert error is None
    assert isinstance(subscription_id, str)
    mock_db['subscriptions'].insert_one.assert_called_once()
    inserted_data = mock_db['subscriptions'].insert_one.call_args[0][0]
    assert inserted_data['customer_id'] == customer_id
    assert inserted_data['product_id'] == product_id
    assert inserted_data['price_at_subscription'] == 10.0
    assert inserted_data['periodicity_at_subscription'] == "monthly"


def test_subscribe_customer_to_product_customer_not_found(mock_db):
    """
    Verifica que la suscripción falla si el cliente no es encontrado.
    """
    product_id = ObjectId()
    mock_db['customers'].find_one.return_value = None 
    mock_db['products'].find_one.return_value = {
        "_id": product_id, "name": "Basic Plan", "price": 10.0, "periodicity": "monthly", "customizable": False
    }

    subscription_service = SubscriptionService(mock_db['db'])
    expiration_date = (datetime.utcnow() + timedelta(days=30)).isoformat()
    subscription_id, error = subscription_service.subscribe_customer_to_product(
        str(ObjectId()), str(product_id), expiration_date, None
    )

    assert subscription_id is None
    assert "Customer not found" in error
    mock_db['subscriptions'].insert_one.assert_not_called()

def test_subscribe_customer_to_product_product_not_found(mock_db):
    """
    Verifica que la suscripción falla si el producto no es encontrado.
    """
    customer_id = ObjectId()
    mock_db['customers'].find_one.return_value = {"_id": customer_id, "email": "test@example.com"}
    mock_db['products'].find_one.return_value = None 

    subscription_service = SubscriptionService(mock_db['db'])
    expiration_date = (datetime.utcnow() + timedelta(days=30)).isoformat()
    subscription_id, error = subscription_service.subscribe_customer_to_product(
        str(customer_id), str(ObjectId()), expiration_date, None
    )

    assert subscription_id is None
    assert "Product not found" in error
    mock_db['subscriptions'].insert_one.assert_not_called()

def test_subscribe_customer_to_product_already_active_subscription(mock_db):
    """
    Verifica que la suscripción falla si ya existe una suscripción activa para el cliente y producto.
    """
    customer_id = ObjectId()
    product_id = ObjectId()
    
    mock_db['customers'].find_one.return_value = {"_id": customer_id, "email": "test@example.com"}
    mock_db['products'].find_one.return_value = {
        "_id": product_id, "name": "Basic Plan", "price": 10.0, "periodicity": "monthly", "customizable": False
    }
    mock_db['subscriptions'].find_one.return_value = {
        "customer_id": customer_id,
        "product_id": product_id,
        "expiration_date": datetime.utcnow() + timedelta(days=5) 
    }

    subscription_service = SubscriptionService(mock_db['db'])
    expiration_date = (datetime.utcnow() + timedelta(days=30)).isoformat()
    subscription_id, error = subscription_service.subscribe_customer_to_product(
        str(customer_id), str(product_id), expiration_date, None
    )

    assert subscription_id is None
    assert "Customer already has an active subscription for this product" in error
    mock_db['subscriptions'].insert_one.assert_not_called()

def test_subscribe_customer_to_product_invalid_date_format(mock_db):
    """
    Verifica que la suscripción falla con un formato de fecha de expiración inválido.
    """
    customer_id = ObjectId()
    product_id = ObjectId()
    
    mock_db['customers'].find_one.return_value = {"_id": customer_id, "email": "test@example.com"}
    mock_db['products'].find_one.return_value = {
        "_id": product_id, "name": "Basic Plan", "price": 10.0, "periodicity": "monthly", "customizable": False
    }

    subscription_service = SubscriptionService(mock_db['db'])
    invalid_expiration_date = "invalid-date"
    
    subscription_id, error = subscription_service.subscribe_customer_to_product(
        str(customer_id), str(product_id), invalid_expiration_date, None
    )

    assert subscription_id is None
    assert "Invalid expiration date format. Use ISO format (YYYY-MM-DDTHH:MM:SS)." in error
    mock_db['subscriptions'].insert_one.assert_not_called()

def test_subscribe_customer_to_product_expiration_date_in_past(mock_db):
    """
    Verifica que la suscripción falla si la fecha de expiración está en el pasado.
    """
    customer_id = ObjectId()
    product_id = ObjectId()
    
    mock_db['customers'].find_one.return_value = {"_id": customer_id, "email": "test@example.com"}
    mock_db['products'].find_one.return_value = {
        "_id": product_id, "name": "Basic Plan", "price": 10.0, "periodicity": "monthly", "customizable": False
    }
    mock_db['subscriptions'].find_one.return_value = None

    subscription_service = SubscriptionService(mock_db['db'])
    past_expiration_date = (datetime.utcnow() - timedelta(days=5)).isoformat()
    
    subscription_id, error = subscription_service.subscribe_customer_to_product(
        str(customer_id), str(product_id), past_expiration_date, None
    )

    assert subscription_id is None
    assert "Expiration date cannot be in the past" in error
    mock_db['subscriptions'].insert_one.assert_not_called()

def test_subscribe_customer_to_product_customizable_missing_customization(mock_db):
    """
    Verifica que la suscripción falla si el producto es personalizable pero no se proporciona personalización.
    """
    customer_id = ObjectId()
    product_id = ObjectId()
    
    mock_db['customers'].find_one.return_value = {"_id": customer_id, "email": "test@example.com"}
    mock_db['products'].find_one.return_value = {
        "_id": product_id, "name": "Customizable Plan", "price": 20.0, "periodicity": "monthly", "customizable": True
    }
    mock_db['subscriptions'].find_one.return_value = None
    mock_db['subscriptions'].insert_one.return_value.inserted_id = ObjectId()

    subscription_service = SubscriptionService(mock_db['db'])
    expiration_date = (datetime.utcnow() + timedelta(days=30)).isoformat()
    
    subscription_id, error = subscription_service.subscribe_customer_to_product(
        str(customer_id), str(product_id), expiration_date, None 
    )

    assert subscription_id is None
    assert "Product is customizable, but no customization data provided" in error
    mock_db['subscriptions'].insert_one.assert_not_called()

def test_subscribe_customer_to_product_non_customizable_with_customization(mock_db):
    """
    Verifica que la suscripción falla si el producto no es personalizable pero se proporciona personalización.
    """
    customer_id = ObjectId()
    product_id = ObjectId()
    
    mock_db['customers'].find_one.return_value = {"_id": customer_id, "email": "test@example.com"}
    mock_db['products'].find_one.return_value = {
        "_id": product_id, "name": "Non-Customizable Plan", "price": 10.0, "periodicity": "monthly", "customizable": False
    }
    mock_db['subscriptions'].find_one.return_value = None
    mock_db['subscriptions'].insert_one.return_value.inserted_id = ObjectId()

    subscription_service = SubscriptionService(mock_db['db'])
    expiration_date = (datetime.utcnow() + timedelta(days=30)).isoformat()
    
    subscription_id, error = subscription_service.subscribe_customer_to_product(
        str(customer_id), str(product_id), expiration_date, {"color": "blue"} 
    )

    assert subscription_id is None
    assert "Product is not customizable, but customization data was provided" in error
    mock_db['subscriptions'].insert_one.assert_not_called()

def test_get_subscription_status_active(mock_db):
    """
    Verifica que el estado de una suscripción activa es 'active'.
    """
    subscription_id = ObjectId()
    mock_db['subscriptions'].find_one.return_value = {
        "_id": subscription_id,
        "expiration_date": datetime.utcnow() + timedelta(days=5)
    }
    subscription_service = SubscriptionService(mock_db['db'])
    status, error = subscription_service.get_subscription_status(str(subscription_id))
    assert error is None
    assert status == "active"

def test_get_subscription_status_expired(mock_db):
    """
    Verifica que el estado de una suscripción expirada es 'expired'.
    """
    subscription_id = ObjectId()
    mock_db['subscriptions'].find_one.return_value = {
        "_id": subscription_id,
        "expiration_date": datetime.utcnow() - timedelta(days=5)
    }
    subscription_service = SubscriptionService(mock_db['db'])
    status, error = subscription_service.get_subscription_status(str(subscription_id))
    assert error is None
    assert status == "expired"

def test_get_subscription_status_not_found(mock_db):
    """
    Verifica que el estado de una suscripción no encontrada devuelve error.
    """
    mock_db['subscriptions'].find_one.return_value = None
    subscription_service = SubscriptionService(mock_db['db'])
    status, error = subscription_service.get_subscription_status(str(ObjectId()))
    assert status is None
    assert "Subscription not found" in error

def test_get_subscription_status_invalid_id(mock_db):
    """
    Verifica que el estado de una suscripción con ID inválido devuelve error.
    """
    subscription_service = SubscriptionService(mock_db['db'])
    status, error = subscription_service.get_subscription_status("invalid_id")
    assert status is None
    assert "Invalid subscription_id format" in error

def test_get_subscription_settings_success(mock_db):
    """
    Verifica que se pueden obtener las configuraciones de una suscripción personalizable.
    """
    subscription_id = ObjectId()
    customization_data = {"color": "red", "size": "large"}
    mock_db['subscriptions'].find_one.return_value = {
        "_id": subscription_id,
        "customization": customization_data,
        "product_id": ObjectId() 
    }
    mock_db['products'].find_one.return_value = {"customizable": True} 

    subscription_service = SubscriptionService(mock_db['db'])
    settings, error = subscription_service.get_subscription_settings(str(subscription_id))
    assert error is None
    assert settings == customization_data

def test_get_subscription_settings_not_customizable(mock_db):
    """
    Verifica que obtener configuraciones de una suscripción no personalizable devuelve un diccionario vacío.
    """
    subscription_id = ObjectId()
    mock_db['subscriptions'].find_one.return_value = {
        "_id": subscription_id,
        "customization": None, 
        "product_id": ObjectId()
    }
    mock_db['products'].find_one.return_value = {"customizable": False} 

    subscription_service = SubscriptionService(mock_db['db'])
    settings, error = subscription_service.get_subscription_settings(str(subscription_id))
    assert "Product associated with this subscription is not customizable." in error
    assert settings == None 

def test_get_subscription_settings_not_found(mock_db):
    """
    Verifica que obtener configuraciones de una suscripción no encontrada devuelve error.
    """
    mock_db['subscriptions'].find_one.return_value = None
    subscription_service = SubscriptionService(mock_db['db'])
    settings, error = subscription_service.get_subscription_settings(str(ObjectId()))
    assert settings is None
    assert "Subscription not found" in error

def test_edit_subscription_settings_success(mock_db):
    """
    Verifica que se pueden editar las configuraciones de una suscripción personalizable.
    """
    subscription_id = ObjectId()
    initial_customization = {"color": "red"}
    new_settings = {"size": "large"}
    
    mock_db['subscriptions'].find_one.return_value = {
        "_id": subscription_id,
        "customization": initial_customization,
        "product_id": ObjectId()
    }
    mock_db['products'].find_one.return_value = {"customizable": True}
    mock_db['subscriptions'].update_one.return_value.modified_count = 1

    subscription_service = SubscriptionService(mock_db['db'])
    success, error = subscription_service.edit_subscription_settings(str(subscription_id), new_settings)
    
    assert success is True
    assert error is None
    mock_db['subscriptions'].update_one.assert_called_once()
    assert mock_db['subscriptions'].update_one.call_args[0][1]['$set']['customization'] == new_settings

def test_edit_subscription_settings_already_up_to_date(mock_db):
    """
    Verifica que no se actualiza si las configuraciones ya están al día.
    """
    subscription_id = ObjectId()
    current_customization = {"color": "red", "size": "large"}
    new_settings = {"size": "large", "color": "red"}

    mock_db['subscriptions'].find_one.return_value = {
        "_id": subscription_id,
        "customization": current_customization,
        "product_id": ObjectId()
    }
    mock_db['products'].find_one.return_value = {"customizable": True}
    mock_db['subscriptions'].update_one.return_value.modified_count = 0 
    mock_db['subscriptions'].update_one.return_value.matched_count = 1 

    subscription_service = SubscriptionService(mock_db['db'])
    success, error = subscription_service.edit_subscription_settings(str(subscription_id), new_settings)
    
    assert success is True 
    assert "Settings already up to date, no changes made" in error 

def test_edit_subscription_settings_not_customizable(mock_db):
    """
    Verifica que no se pueden editar las configuraciones de una suscripción no personalizable.
    """
    subscription_id = ObjectId()
    mock_db['subscriptions'].find_one.return_value = {
        "_id": subscription_id,
        "customization": None,
        "product_id": ObjectId()
    }
    mock_db['products'].find_one.return_value = {"customizable": False}

    subscription_service = SubscriptionService(mock_db['db'])
    success, error = subscription_service.edit_subscription_settings(str(subscription_id), {"color": "blue"})
    
    assert success is False
    assert "Product associated with this subscription is not customizable" in error
    mock_db['subscriptions'].update_one.assert_not_called()

def test_extend_subscription_success(mock_db):
    """
    Verifica que se puede extender la fecha de expiración de una suscripción.
    """
    subscription_id = ObjectId()
    old_expiration = datetime.utcnow() + timedelta(days=10)
    new_expiration = old_expiration + timedelta(days=30)
    
    mock_db['subscriptions'].find_one.return_value = {
        "_id": subscription_id,
        "expiration_date": old_expiration
    }
    mock_db['subscriptions'].update_one.return_value.modified_count = 1

    subscription_service = SubscriptionService(mock_db['db'])
    success, error = subscription_service.extend_subscription(str(subscription_id), new_expiration.isoformat())
    
    assert success is True
    assert error is None
    mock_db['subscriptions'].update_one.assert_called_once()
    updated_date = mock_db['subscriptions'].update_one.call_args[0][1]['$set']['expiration_date']
    assert int(updated_date.timestamp()) == int(new_expiration.timestamp())

def test_extend_subscription_already_extended(mock_db):
    """
    Verifica que no se extiende si la nueva fecha no es posterior a la actual.
    """
    subscription_id = ObjectId()
    current_expiration = datetime.utcnow() + timedelta(days=30)
    new_expiration = current_expiration - timedelta(days=5)
    
    mock_db['subscriptions'].find_one.return_value = {
        "_id": subscription_id,
        "expiration_date": current_expiration
    }
    mock_db['subscriptions'].update_one.return_value.modified_count = 0 

    subscription_service = SubscriptionService(mock_db['db'])
    success, error = subscription_service.extend_subscription(str(subscription_id), new_expiration.isoformat())
    
    assert success is False 
    assert "Subscription expiration date already set to this value or later" in error
    mock_db['subscriptions'].update_one.assert_not_called() 

def test_extend_subscription_invalid_date_format(mock_db):
    """
    Verifica que la extensión falla con un formato de fecha inválido.
    """
    subscription_id = ObjectId()
    mock_db['subscriptions'].find_one.return_value = {
        "_id": subscription_id,
        "expiration_date": datetime.utcnow() + timedelta(days=10)
    }

    subscription_service = SubscriptionService(mock_db['db'])
    success, error = subscription_service.extend_subscription(str(subscription_id), "invalid-date")
    
    assert success is False
    assert "Invalid new expiration date format. Use ISO format (YYYY-MM-DDTHH:MM:SS)." in error
    mock_db['subscriptions'].update_one.assert_not_called()

def test_extend_subscription_date_in_past(mock_db):
    """
    Verifica que la extensión falla si la nueva fecha está en el pasado.
    """
    subscription_id = ObjectId()
    mock_db['subscriptions'].find_one.return_value = {
        "_id": subscription_id,
        "expiration_date": datetime.utcnow() + timedelta(days=10)
    }

    subscription_service = SubscriptionService(mock_db['db'])
    past_date = datetime.utcnow() - timedelta(days=1)
    success, error = subscription_service.extend_subscription(str(subscription_id), past_date.isoformat())
    
    assert success is False
    assert "New expiration date cannot be in the past" in error
    mock_db['subscriptions'].update_one.assert_not_called()

def test_get_subscription_by_id_success(mock_db):
    """
    Verifica que se puede obtener una suscripción por su ID.
    """
    subscription_id = ObjectId()
    mock_subscription = {"_id": subscription_id, "customer_id": ObjectId(), "product_id": ObjectId()}
    mock_db['subscriptions'].find_one.return_value = mock_subscription

    subscription_service = SubscriptionService(mock_db['db'])
    subscription = subscription_service.get_subscription_by_id(str(subscription_id))

    assert subscription is not None
    assert str(subscription["_id"]) == str(subscription_id)

def test_get_subscription_by_id_not_found(mock_db):
    """
    Verifica que obtener una suscripción por ID devuelve None si no se encuentra.
    """
    mock_db['subscriptions'].find_one.return_value = None
    subscription_service = SubscriptionService(mock_db['db'])
    subscription = subscription_service.get_subscription_by_id(str(ObjectId()))
    assert subscription is None

def test_get_subscription_by_id_invalid_id(mock_db):
    """
    Verifica que obtener una suscripción por ID devuelve None si el ID es inválido.
    """
    subscription_service = SubscriptionService(mock_db['db'])
    subscription = subscription_service.get_subscription_by_id("invalid_id")
    assert subscription is None
