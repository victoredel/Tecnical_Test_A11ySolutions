from database import get_db
from models.customer import customer_model
from models.product import product_model
from models.subscription import subscription_model
from bson import ObjectId
from datetime import datetime

class SubscriptionService:
    def __init__(self, db):
        self.db = db
        self.customers_collection = self.db.customers
        self.products_collection = self.db.products
        self.subscriptions_collection = self.db.subscriptions

    def add_product(self, name, description, customizable, price, periodicity):
        if self.products_collection.find_one({"name": name}):
            return None, "Product with this name already exists"
        
        if not isinstance(price, (int, float)) or price <= 0:
            return None, "Price must be a positive number"
        if periodicity not in ["monthly", "annually"]: 
            return None, "Periodicity must be 'monthly' or 'annually'"

        product_data = product_model(name, description, customizable, price, periodicity)
        result = self.products_collection.insert_one(product_data)
        return str(result.inserted_id), None

    def subscribe_customer_to_product(self, customer_id_str, product_id_str, expiration_date_str, customization=None):
        """
        Suscribe a un cliente a un producto
        """
        try:
            customer_id = ObjectId(customer_id_str)
            product_id = ObjectId(product_id_str)
        except Exception:
            return None, "Invalid customer_id or product_id format"

        customer = self.customers_collection.find_one({"_id": customer_id})
        if not customer:
            return None, "Customer not found"

        product = self.products_collection.find_one({"_id": product_id})
        if not product:
            return None, "Product not found"

        try:
            expiration_date = datetime.fromisoformat(expiration_date_str)
            if expiration_date.tzinfo is None:
                expiration_date = expiration_date.replace(tzinfo=None)
            if expiration_date < datetime.utcnow():
                 return None, "Expiration date cannot be in the past"
        except ValueError:
            return None, "Invalid expiration date format. Use ISO format (YYYY-MM-DDTHH:MM:SS)."

        active_subscription = self.subscriptions_collection.find_one({
            "customer_id": customer_id,
            "product_id": product_id,
            "expiration_date": {"$gt": datetime.utcnow()}
        })
        if active_subscription:
            return None, "Customer already has an active subscription for this product"

        if product.get("customizable") and customization is None:
            return None, "Product is customizable, but no customization data provided"
        if not product.get("customizable") and customization is not None:
            return None, "Product is not customizable, but customization data was provided"
        
        subscription_price = product.get("price")
        subscription_periodicity = product.get("periodicity")

        if subscription_price is None or subscription_periodicity is None:
            return None, "Product is missing price or periodicity data." 


        subscription_data = subscription_model(
            customer_id=customer_id,
            product_id=product_id,
            expiration_date=expiration_date,
            customization=customization,
            price_at_subscription=subscription_price, 
            periodicity_at_subscription=subscription_periodicity, 
            start_date=datetime.utcnow()
        )
        result = self.subscriptions_collection.insert_one(subscription_data)
        return str(result.inserted_id), None

    def get_subscription_status(self, subscription_id_str):
        if not ObjectId.is_valid(subscription_id_str):
            return None, "Invalid subscription_id format."

        subscription = self.subscriptions_collection.find_one({"_id": ObjectId(subscription_id_str)})
        if not subscription:
            return None, "Subscription not found."

        status = "active" if subscription["expiration_date"] > datetime.now() else "expired"
        return status, None

    def get_subscription_settings(self, subscription_id_str):
        if not ObjectId.is_valid(subscription_id_str):
            return None, "Invalid subscription_id format."

        subscription = self.subscriptions_collection.find_one({"_id": ObjectId(subscription_id_str)})
        if not subscription:
            return None, "Subscription not found."
        
        product = self.products_collection.find_one({"_id": subscription["product_id"]})
        if not product or not product.get("customizable", False):
            return None, "Product associated with this subscription is not customizable."

        return subscription.get("customization", {}), None

    def edit_subscription_settings(self, subscription_id_str, new_settings):
        if not ObjectId.is_valid(subscription_id_str):
            return False, "Invalid subscription_id format."

        subscription_id = ObjectId(subscription_id_str)
        subscription = self.subscriptions_collection.find_one({"_id": subscription_id})
        if not subscription:
            return False, "Subscription not found."
        
        product = self.products_collection.find_one({"_id": subscription["product_id"]})
        if not product or not product.get("customizable", False):
            return False, "Product associated with this subscription is not customizable, settings cannot be edited."

        result = self.subscriptions_collection.update_one(
            {"_id": subscription_id},
            {"$set": {"customization": new_settings}}
        )
        if result.modified_count == 1:
            return True, None
        elif result.matched_count == 1: 
            return True, "Settings already up to date, no changes made"
        return False, "Failed to update subscription settings."

    def extend_subscription(self, subscription_id_str, new_expiration_date_str):
        if not ObjectId.is_valid(subscription_id_str):
            return False, "Invalid subscription_id format."

        try:
            new_expiration_date = datetime.fromisoformat(new_expiration_date_str)
        except ValueError:
            return False, "Invalid new expiration date format. Use ISO format (YYYY-MM-DDTHH:MM:SS)."

        if new_expiration_date < datetime.utcnow():
            return False, "New expiration date cannot be in the past."
        
        subscription_id = ObjectId(subscription_id_str)
        
        subscription = self.subscriptions_collection.find_one({"_id": subscription_id})
        
        if subscription and subscription["expiration_date"] > new_expiration_date:
            return False, "Subscription expiration date already set to this value or later"
        if not subscription:
            return False, "Subscription not found."

        result = self.subscriptions_collection.update_one(
            {"_id": subscription_id},
            {"$set": {"expiration_date": new_expiration_date}}
        )

        if result.modified_count == 1:
            return True, None
        elif result.matched_count == 1:
            return True, "Subscription expiration date already set to this value"
        return False, "Failed to extend subscription."
    def get_subscription_by_id(self, subscription_id_str):
        """
        Retorna un documento de suscripción por su ID.
        """
        try:
            subscription_id = ObjectId(subscription_id_str)
        except Exception:
            return None 
        
        return self.subscriptions_collection.find_one({"_id": subscription_id})