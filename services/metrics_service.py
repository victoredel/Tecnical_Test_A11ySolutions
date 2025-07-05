from database import get_db
from datetime import datetime, timedelta, timezone
from bson import ObjectId

class MetricsService:
    def __init__(self, db):
        self.db = db
        self.customers_collection = self.db.customers
        self.subscriptions_collection = self.db.subscriptions

    def get_active_subscriptions_in_period(self, start_date, end_date):
        """
        Obtiene suscripciones activas en un periodo dado.
        """
        return list(self.subscriptions_collection.find({
            "start_date": {"$lte": end_date},
            "expiration_date": {"$gt": start_date}
        }))

    def calculate_mrr(self):
        """
        Calcula el Ingreso Recurrente Mensual (MRR) actual.
        """
        mrr = 0.0
        active_subscriptions = self.subscriptions_collection.find({
            "expiration_date": {"$gt": datetime.utcnow()}
        })

        for sub in active_subscriptions:
            price = sub.get("price_at_subscription")
            periodicity = sub.get("periodicity_at_subscription")

            if price is None or periodicity is None:
                continue 

            if periodicity == "monthly":
                mrr += price
            elif periodicity == "annually":
                mrr += (price / 12.0)
        return round(mrr, 2)

    def calculate_arr(self):
        """
        Calcula el Ingreso Recurrente Anual (ARR) actual.
        MRR * 12.
        """
        mrr = self.calculate_mrr()
        arr = mrr * 12.0
        return round(arr, 2)

    def calculate_arpu(self):
        """
        Calcula el Ingreso Medio por Usuario (ARPU) actual.
        """
        mrr = self.calculate_mrr()
        
        active_customer_ids = self.subscriptions_collection.distinct(
            "customer_id",
            {"expiration_date": {"$gt": datetime.utcnow()}}
        )
        num_active_customers = len(active_customer_ids)

        if num_active_customers == 0:
            return 0.0
        
        arpu = mrr / num_active_customers
        return round(arpu, 2)

    def calculate_customer_retention_rate(self, start_date, end_date):
        """
        Calcula la Tasa de Retención de Clientes (CRR) para un período dado.
        """
        customers_at_start_period = self.subscriptions_collection.distinct(
            "customer_id",
            {"start_date": {"$lte": start_date}, "expiration_date": {"$gt": start_date}}
        )
        
        customers_at_end_period = self.subscriptions_collection.distinct(
            "customer_id",
            {"start_date": {"$lte": end_date}, "expiration_date": {"$gt": end_date}}
        )

        new_customers_in_period = self.subscriptions_collection.distinct(
            "customer_id",
            {"start_date": {"$gte": start_date, "$lte": end_date}}
        )
        
        set_customers_at_start = set(customers_at_start_period)
        set_customers_at_end = set(customers_at_end_period)
        set_new_customers = set(new_customers_in_period)

        retained_customers = set_customers_at_start.intersection(set_customers_at_end)
        
        customers_at_end_excluding_new = set_customers_at_end.difference(set_new_customers)
        
        num_customers_at_start = len(set_customers_at_start)
        num_customers_at_end = len(set_customers_at_end)
        num_new_customers = len(set_new_customers)

        if num_customers_at_start == 0:
            return 0.0 
        retained_customers_for_formula = len(set_customers_at_end.difference(set_new_customers))

        crr = (retained_customers_for_formula / num_customers_at_start) * 100
        return round(crr, 2)


    def calculate_churn_rate(self, start_date, end_date):
        """
        Calcula la Tasa de Abandono (Churn Rate - CR) para un período dado.
        """
        customers_at_start_period = self.subscriptions_collection.distinct(
            "customer_id",
            {"start_date": {"$lte": start_date}, "expiration_date": {"$gt": start_date}}
        )
        
        customers_at_end_period = self.subscriptions_collection.distinct(
            "customer_id",
            {"start_date": {"$lte": end_date}, "expiration_date": {"$gt": end_date}}
        )

        set_customers_at_start = set(customers_at_start_period)
        set_customers_at_end = set(customers_at_end_period)

        num_customers_at_start = len(set_customers_at_start)
        
        if num_customers_at_start == 0:
            return 0.0

        lost_customers = set_customers_at_start.difference(set_customers_at_end)
        num_lost_customers = len(lost_customers)

        churn_rate = (num_lost_customers / num_customers_at_start) * 100
        return round(churn_rate, 2)

    def calculate_aov(self):
        """
        Calcula el Valor Promedio del Pedido (AOV).
        """
        pipeline = [
            {"$match": {"price_at_subscription": {"$exists": True, "$ne": None}}},
            {"$group": {
                "_id": None, 
                "total_revenue": {"$sum": "$price_at_subscription"},
                "total_subscriptions": {"$sum": 1}
            }}
        ]
        
        result = list(self.subscriptions_collection.aggregate(pipeline))
        
        if result and result[0]["total_subscriptions"] > 0:
            aov = result[0]["total_revenue"] / result[0]["total_subscriptions"]
            return round(aov, 2)
        return 0.0

    def calculate_rpr(self):
        """
        Calcula la Tasa de Compra Repetida (RPR).
        """
        pipeline = [
            {"$group": {
                "_id": "$customer_id", 
                "subscription_count": {"$sum": 1} 
            }},
            {"$match": {
                "subscription_count": {"$gt": 1} 
            }},
            {"$count": "repeat_customers"}
        ]
        repeat_customers_result = list(self.subscriptions_collection.aggregate(pipeline))
        num_repeat_customers = repeat_customers_result[0]["repeat_customers"] if repeat_customers_result else 0

        total_customers_with_subscriptions = self.subscriptions_collection.distinct("customer_id")
        num_total_customers = len(total_customers_with_subscriptions)

        if num_total_customers == 0:
            return 0.0
        
        rpr = (num_repeat_customers / num_total_customers) * 100
        return round(rpr, 2)
    
    def calculate_purchase_frequency(self):
        """
        Calcula la frecuencia de compra promedio (suscripciones por cliente).
        """
        total_subscriptions_pipeline = [
            {"$group": {
                "_id": None,
                "count": {"$sum": 1}
            }}
        ]
        total_subscriptions_result = list(self.subscriptions_collection.aggregate(total_subscriptions_pipeline))
        num_total_subscriptions = total_subscriptions_result[0]["count"] if total_subscriptions_result else 0

        total_customers_with_subscriptions = self.subscriptions_collection.distinct("customer_id")
        num_total_customers = len(total_customers_with_subscriptions)

        if num_total_customers == 0:
            return 0.0
        
        purchase_frequency = num_total_subscriptions / num_total_customers
        return round(purchase_frequency, 2)