def product_model(name, description, customizable, price, periodicity):
    """
    Define la estructura del documento para un producto.
    price: El precio del producto.
    periodicity: La frecuencia de pago (e.g., "monthly", "annually").
    """
    return {
        "name": name,
        "description": description,
        "customizable": customizable,
        "price": price,         
        "periodicity": periodicity 
    }
