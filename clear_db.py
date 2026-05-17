from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017")
db = client["fulfillment_db"]

print("Clearing orders...")
db.orders.delete_many({})

print("Clearing notifications...")
db.notifications.delete_many({})

print("Clearing logs...")
db.logs.delete_many({})

print("Database cleared successfully!")