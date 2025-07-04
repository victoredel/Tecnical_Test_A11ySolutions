import jwt
from datetime import datetime, timedelta, timezone
from database import get_db
from models.customer import customer_model
from utils.security import hash_password, verify_password
from config import Config

class AuthService:
    def __init__(self):
        self.db = get_db()
        self.customers_collection = self.db.customers

    def register_customer(self, name, email, password):
        if self.customers_collection.find_one({"email": email}):
            return None, "Customer with this email already exists"
        
        hashed_password = hash_password(password)
        customer_data = customer_model(name, email, hashed_password)
        result = self.customers_collection.insert_one(customer_data)
        return str(result.inserted_id), None

    def login_customer(self, email, password):
        customer = self.customers_collection.find_one({"email": email})
        if not customer:
            return None, "Invalid credentials"

        if not verify_password(password, customer["password_hash"]):
            return None, "Invalid credentials"

        payload = {
            "sub": str(customer["_id"]), 
            "email": customer["email"],
            "exp": datetime.now(timezone.utc) + timedelta(seconds=Config.JWT_ACCESS_TOKEN_EXPIRES_SECONDS)
        }
        
        token = jwt.encode(payload, Config.JWT_SECRET_KEY, algorithm="HS256")
        
        return token, None

    def get_customer_by_id(self, customer_id_str):
        from bson import ObjectId 
        if not ObjectId.is_valid(customer_id_str):
            return None
        return self.customers_collection.find_one({"_id": ObjectId(customer_id_str)})