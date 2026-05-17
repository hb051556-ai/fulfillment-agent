from pymongo import MongoClient
from datetime import datetime

MONGO_URL = "mongodb://localhost:27017"
DB_NAME = "fulfillment_db"

client = MongoClient(MONGO_URL)
db = client[DB_NAME]

sample_orders = [
    {
        "order_id": "ORD-001",
        "customer_name": "Ahmed Raza",
        "sku": "SKU-SHOES-42",
        "address": "Block 5 Clifton Karachi",
        "channel": "whatsapp",
        "sla": "2-day",
        "status": "confirmed",
        "eta": "2026-05-20",
        "notification_count": 0,
        "created_at": datetime.now()
    },
    {
        "order_id": "ORD-002",
        "customer_name": "Sara Khan",
        "sku": "SKU-BAG-08",
        "address": "Gulshan-e-Iqbal Karachi",
        "channel": "sms",
        "sla": "next-day",
        "status": "delayed",
        "eta": "2026-05-22",
        "notification_count": 2,
        "created_at": datetime.now()
    },
    {
        "order_id": "ORD-003",
        "customer_name": "Ali Hassan",
        "sku": "SKU-WATCH-15",
        "address": "DHA Phase 6 Karachi",
        "channel": "email",
        "sla": "standard",
        "status": "delivered",
        "eta": "2026-05-15",
        "notification_count": 3,
        "created_at": datetime.now()
    }
]

sample_notifications = [
    {
        "order_id": "ORD-001",
        "customer": "Ahmed Raza",
        "channel": "whatsapp",
        "message": "Assalam o Alaikum Ahmed Raza! Aapka order confirm ho gaya.",
        "sent_at": datetime.now()
    }
]

print("Inserting sample orders...")
db.orders.insert_many(sample_orders)

print("Inserting sample notifications...")
db.notifications.insert_many(sample_notifications)

print("Creating indexes...")
db.orders.create_index("order_id", unique=True)
db.notifications.create_index("order_id")
db.logs.create_index("order_id")

print("Database setup complete!")