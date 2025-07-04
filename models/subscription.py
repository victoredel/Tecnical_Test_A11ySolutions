def subscription_model(customer_id, product_id, expiration_date, customization=None):
    return {
        "customer_id": customer_id, 
        "product_id": product_id,   
        "expiration_date": expiration_date, 
        "customization": customization if customization is not None else {}
    }

# Ejemplo de estructura para un "widget de accesibilidad"
def accessibility_widget_customization_example():
    return {
        "topBarColor": "#FFFFFF",
        "topBarBackgroundColor": "#1A1A1A",
        "positionIndex": 1, 
        "defaultLang": "es"
    }