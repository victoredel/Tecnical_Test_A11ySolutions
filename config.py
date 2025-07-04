import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
    MONGO_DB_NAME = os.getenv("MONGO_DB_NAME", "subscription_manager")
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "vbocfklifuoltv;jutdcvidickluyszxcidxk")
    JWT_ACCESS_TOKEN_EXPIRES_SECONDS = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRES_SECONDS", 3600)) # 1 hora