from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
from datetime import datetime

MONGO_URL = "mongodb://localhost:27017"
DB_NAME = "fulfillment_db"

client = None
db = None


def serialize_doc(doc):
    if doc is None:
        return None
    result = {}
    for key, value in doc.items():
        if isinstance(value, ObjectId):
            result[key] = str(value)
        elif isinstance(value, datetime):
            result[key] = value.isoformat()
        elif isinstance(value, dict):
            result[key] = serialize_doc(value)
        elif isinstance(value, list):
            result[key] = [serialize_doc(item) if isinstance(item, dict) else item for item in value]
        else:
            result[key] = value
    return result


async def connect_db():
    global client, db
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    await db.orders.create_index("order_id", unique=True)
    await db.notifications.create_index("order_id")
    await db.logs.create_index("order_id")


async def close_db():
    global client
    if client:
        client.close()


async def get_all_orders():
    docs = await db.orders.find().to_list(length=None)
    return [serialize_doc(doc) for doc in docs]


async def get_order_by_id(order_id):
    doc = await db.orders.find_one({"order_id": order_id})
    return serialize_doc(doc) if doc else None


async def insert_order(data: dict):
    data["created_at"] = datetime.now()
    data["notification_count"] = 0
    await db.orders.insert_one(data)


async def update_order(order_id, update_data: dict):
    await db.orders.update_one(
        {"order_id": order_id},
        {"$set": update_data}
    )


async def insert_notification(data: dict):
    data["sent_at"] = datetime.now()
    await db.notifications.insert_one(data)


async def get_all_notifications():
    docs = await db.notifications.find().sort("sent_at", -1).to_list(length=None)
    return [serialize_doc(doc) for doc in docs]


async def insert_log(data: dict):
    data["timestamp"] = datetime.now()
    await db.logs.insert_one(data)


async def get_notification_count(order_id) -> int:
    return await db.notifications.count_documents({"order_id": order_id})


async def delete_order(order_id) -> bool:
    result = await db.orders.delete_one({"order_id": order_id})
    return result.deleted_count > 0