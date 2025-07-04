def customer_model(name, email, password_hash):
    return {
        "name": name,
        "email": email,
        "password_hash": password_hash
    }