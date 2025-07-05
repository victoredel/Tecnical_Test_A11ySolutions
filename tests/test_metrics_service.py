import pytest
from services.metrics_service import MetricsService
from bson import ObjectId
from datetime import datetime, timedelta, timezone 

def create_mock_subscription(
    customer_id, 
    product_id, 
    price, 
    periodicity, 
    start_date, 
    expiration_date, 
    customization=None
):
    return {
        "_id": ObjectId(),
        "customer_id": customer_id,
        "product_id": product_id,
        "price_at_subscription": price,
        "periodicity_at_subscription": periodicity,
        "start_date": start_date,
        "expiration_date": expiration_date,
        "customization": customization
    }

def test_calculate_mrr_no_active_subscriptions(mock_db):
    """
    Verifica que el MRR es 0.0 si no hay suscripciones activas.
    """
    mock_db['subscriptions'].find.return_value = [] 
    metrics_service = MetricsService(mock_db['db'])
    mrr = metrics_service.calculate_mrr()
    assert mrr == 0.0

def test_calculate_mrr_with_monthly_subscriptions(mock_db):
    """
    Verifica el cálculo del MRR con suscripciones mensuales activas.
    """
    now = datetime.utcnow() 
    
    subscriptions = [
        create_mock_subscription(ObjectId(), ObjectId(), 100.0, "monthly", now - timedelta(days=5), now + timedelta(days=25)),
        create_mock_subscription(ObjectId(), ObjectId(), 50.0, "monthly", now - timedelta(days=10), now + timedelta(days=20)),
    ]
    mock_db['subscriptions'].find.return_value = iter(subscriptions)
    
    metrics_service = MetricsService(mock_db['db'])
    mrr = metrics_service.calculate_mrr()
    assert mrr == 150.0

def test_calculate_mrr_with_annual_subscriptions(mock_db): 
    """
    Verifica el cálculo del MRR con suscripciones anuales activas.
    """
    now = datetime.utcnow()
    
    subscriptions = [
        create_mock_subscription(ObjectId(), ObjectId(), 1200.0, "annually", now - timedelta(days=5), now + timedelta(days=360)), 
        create_mock_subscription(ObjectId(), ObjectId(), 600.0, "annually", now - timedelta(days=10), now + timedelta(days=350)), 
    ]
    mock_db['subscriptions'].find.return_value = iter(subscriptions)
    
    metrics_service = MetricsService(mock_db['db'])
    mrr = metrics_service.calculate_mrr()
    assert mrr == 150.0 

def test_calculate_mrr_mixed_subscriptions(mock_db):
    """
    Verifica el cálculo del MRR.
    """
    now = datetime.utcnow()
    
    subscriptions = [
        create_mock_subscription(ObjectId(), ObjectId(), 100.0, "monthly", now - timedelta(days=5), now + timedelta(days=25)),
        create_mock_subscription(ObjectId(), ObjectId(), 1200.0, "annually", now - timedelta(days=10), now + timedelta(days=350)), 
        create_mock_subscription(ObjectId(), ObjectId(), 75.0, "monthly", now - timedelta(days=2), now + timedelta(days=28)),
    ]
    mock_db['subscriptions'].find.return_value = iter(subscriptions)
    
    metrics_service = MetricsService(mock_db['db'])
    mrr = metrics_service.calculate_mrr()
    assert mrr == 275.0 

def test_calculate_arr(mock_db):
    """
    Verifica el cálculo del ARR (MRR * 12).
    """
    now = datetime.utcnow()
    
    subscriptions = [
        create_mock_subscription(ObjectId(), ObjectId(), 100.0, "monthly", now - timedelta(days=5), now + timedelta(days=25)),
    ]
    mock_db['subscriptions'].find.return_value = iter(subscriptions)
    
    metrics_service = MetricsService(mock_db['db'])
    arr = metrics_service.calculate_arr()
    assert arr == 1200.0 

def test_calculate_arpu_no_active_customers(mock_db): 
    """
    Verifica que el ARPU es 0.0 si no hay clientes activos.
    """
    now = datetime.utcnow()
    
    mock_db['subscriptions'].find.return_value = []
    mock_db['subscriptions'].distinct.return_value = []
    metrics_service = MetricsService(mock_db['db'])
    arpu = metrics_service.calculate_arpu()
    assert arpu == 0.0

def test_calculate_arpu_with_active_customers(mock_db): 
    """
    Verifica el cálculo del ARPU con clientes activos.
    """
    now = datetime.utcnow()
    
    customer1_id = ObjectId()
    customer2_id = ObjectId()

    subscriptions = [
        create_mock_subscription(customer1_id, ObjectId(), 100.0, "monthly", now - timedelta(days=5), now + timedelta(days=25)),
        create_mock_subscription(customer2_id, ObjectId(), 50.0, "monthly", now - timedelta(days=10), now + timedelta(days=20)),
        create_mock_subscription(customer1_id, ObjectId(), 20.0, "monthly", now - timedelta(days=1), now + timedelta(days=29)), 
    ]
    mock_db['subscriptions'].find.return_value = iter(subscriptions)
    mock_db['subscriptions'].distinct.return_value = [customer1_id, customer2_id] 
    
    metrics_service = MetricsService(mock_db['db'])
    arpu = metrics_service.calculate_arpu()
    assert arpu == 85.0

def test_calculate_customer_retention_rate_no_customers_at_start(mock_db):
    """
    Verifica que la Tasa de Retención es 0.0 si no hay clientes al inicio del período.
    """
    start_date = datetime(2024, 1, 1)
    end_date = datetime(2024, 1, 31)
    mock_db['subscriptions'].distinct.return_value = [] 
    metrics_service = MetricsService(mock_db['db'])
    crr = metrics_service.calculate_customer_retention_rate(start_date, end_date)
    assert crr == 0.0

def test_calculate_customer_retention_rate_basic(mock_db):
    """
    Verifica el cálculo básico de la Tasa de Retención de Clientes.
    """
    customer1_id = ObjectId()
    customer2_id = ObjectId()
    customer3_id = ObjectId()

    start_date = datetime(2024, 1, 1, tzinfo=timezone.utc)
    end_date = datetime(2024, 1, 31, tzinfo=timezone.utc)

    mock_db['subscriptions'].distinct.side_effect = [
        [customer1_id, customer2_id],
        [customer1_id, customer3_id],
        [customer3_id] 
    ]
    
    metrics_service = MetricsService(mock_db['db'])
    crr = metrics_service.calculate_customer_retention_rate(start_date, end_date)
    assert crr == 50.0
    
    mock_db['subscriptions'].distinct.side_effect = None


def test_calculate_churn_rate_no_customers_at_start(mock_db):
    """
    Verifica que la Tasa de Abandono es 0.0 si no hay clientes al inicio del período.
    """
    start_date = datetime(2024, 1, 1)
    end_date = datetime(2024, 1, 31)
    mock_db['subscriptions'].distinct.return_value = []
    metrics_service = MetricsService(mock_db['db'])
    churn_rate = metrics_service.calculate_churn_rate(start_date, end_date)
    assert churn_rate == 0.0

def test_calculate_churn_rate_basic(mock_db):
    """
    Verifica el cálculo básico de la Tasa de Abandono.
    """
    customer1_id = ObjectId()
    customer2_id = ObjectId()
    customer3_id = ObjectId() 

    start_date = datetime(2024, 1, 1, tzinfo=timezone.utc)
    end_date = datetime(2024, 1, 31, tzinfo=timezone.utc)

    mock_db['subscriptions'].distinct.side_effect = [
        [customer1_id, customer2_id, customer3_id],
        [customer1_id, customer2_id] 
    ]
    
    metrics_service = MetricsService(mock_db['db'])
    churn_rate = metrics_service.calculate_churn_rate(start_date, end_date)
    assert churn_rate == 33.33
    
    mock_db['subscriptions'].distinct.side_effect = None

def test_calculate_aov_no_subscriptions(mock_db):
    """
    Verifica que el AOV es 0.0 si no hay suscripciones.
    """
    mock_db['subscriptions'].aggregate.return_value = []
    metrics_service = MetricsService(mock_db['db'])
    aov = metrics_service.calculate_aov()
    assert aov == 0.0

def test_calculate_aov_with_subscriptions(mock_db):
    """
    Verifica el cálculo del AOV con suscripciones.
    """
    mock_db['subscriptions'].aggregate.return_value = [
        {"_id": None, "total_revenue": 300.0, "total_subscriptions": 3}
    ]
    metrics_service = MetricsService(mock_db['db'])
    aov = metrics_service.calculate_aov()
    assert aov == 100.0 

def test_calculate_rpr_no_customers(mock_db):
    """
    Verifica que el RPR es 0.0 si no hay clientes con suscripciones.
    """
    mock_db['subscriptions'].aggregate.return_value = [] 
    mock_db['subscriptions'].distinct.return_value = [] 
    metrics_service = MetricsService(mock_db['db'])
    rpr = metrics_service.calculate_rpr()
    assert rpr == 0.0

def test_calculate_rpr_with_repeat_customers(mock_db):
    """
    Verifica el cálculo del RPR con clientes que repiten compra.
    """
    customer1_id = ObjectId()
    customer2_id = ObjectId()
    customer3_id = ObjectId()

    mock_db['subscriptions'].aggregate.side_effect = [
        [{"_id": customer1_id, "subscription_count": 2, "repeat_customers": 1}], 
        [] 
    ]
    mock_db['subscriptions'].distinct.return_value = [customer1_id, customer2_id, customer3_id]
    
    metrics_service = MetricsService(mock_db['db'])
    rpr = metrics_service.calculate_rpr()
    assert rpr == 33.33
    
    mock_db['subscriptions'].aggregate.side_effect = None 

def test_calculate_purchase_frequency_no_subscriptions(mock_db):
    """
    Verifica que la frecuencia de compra es 0.0 si no hay suscripciones.
    """
    mock_db['subscriptions'].aggregate.return_value = []
    mock_db['subscriptions'].distinct.return_value = []
    metrics_service = MetricsService(mock_db['db'])
    frequency = metrics_service.calculate_purchase_frequency()
    assert frequency == 0.0

def test_calculate_purchase_frequency_with_data(mock_db):
    """
    Verifica el cálculo de la frecuencia de compra.
    """
    customer1_id = ObjectId()
    customer2_id = ObjectId()

    mock_db['subscriptions'].aggregate.return_value = [
        {"_id": None, "count": 3} 
    ]
    mock_db['subscriptions'].distinct.return_value = [customer1_id, customer2_id] 
    
    metrics_service = MetricsService(mock_db['db'])
    frequency = metrics_service.calculate_purchase_frequency()
    assert frequency == 1.5
