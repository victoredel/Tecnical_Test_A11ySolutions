from datetime import datetime

def subscription_model(
    customer_id, 
    product_id, 
    expiration_date, 
    customization, 
    price_at_subscription, 
    periodicity_at_subscription, 
    start_date=None
):
    return {
        "customer_id": customer_id,
        "product_id": product_id,
        "expiration_date": expiration_date,
        "customization": customization,
        "price_at_subscription": price_at_subscription,        
        "periodicity_at_subscription": periodicity_at_subscription, 
        "start_date": start_date if start_date is not None else datetime.utcnow() 
    }