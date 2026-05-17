from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import database
import agent
from pydantic import BaseModel


@asynccontextmanager
async def lifespan(app: FastAPI):
    await database.connect_db()
    print("MongoDB connected - Ready!")
    yield
    await database.close_db()


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class OrderRequest(BaseModel):
    order_id: str
    customer_name: str
    sku: str
    address: str
    channel: str
    sla: str
    eta: str


class DelayRequest(BaseModel):
    order_id: str
    new_eta: str


class DeliveredRequest(BaseModel):
    order_id: str


@app.post("/api/order")
async def place_order(order: OrderRequest):
    try:
        order_data = {
            "order_id": order.order_id,
            "customer_name": order.customer_name,
            "sku": order.sku,
            "address": order.address,
            "channel": order.channel,
            "sla": order.sla,
            "status": "confirmed",
            "eta": order.eta
        }
        
        await database.insert_order(order_data)
        
        await agent.run_order_confirmed(
            order.order_id,
            order.customer_name,
            order.channel,
            order.eta
        )
        
        return {"success": True, "order_id": order.order_id, "message": "Order placed and notification sent"}
    except Exception as e:
        return {"success": False, "message": str(e)}


@app.post("/api/delay")
async def trigger_delay(req: DelayRequest):
    try:
        order = await database.get_order_by_id(req.order_id)
        if not order:
            return {"success": False, "message": "Order not found"}
        
        await agent.run_order_delayed(
            req.order_id,
            order["customer_name"],
            order["channel"],
            req.new_eta
        )
        
        return {"success": True, "message": "Order delayed and notification sent"}
    except Exception as e:
        return {"success": False, "message": str(e)}


@app.post("/api/delivered")
async def mark_delivered(req: DeliveredRequest):
    try:
        order = await database.get_order_by_id(req.order_id)
        if not order:
            return {"success": False, "message": "Order not found"}
        
        await agent.run_order_delivered(
            req.order_id,
            order["customer_name"],
            order["channel"]
        )
        
        return {"success": True, "message": "Order delivered and notification sent"}
    except Exception as e:
        return {"success": False, "message": str(e)}


class DeleteRequest(BaseModel):
    order_id: str


@app.post("/api/delete")
async def delete_order(req: DeleteRequest):
    try:
        deleted = await database.delete_order(req.order_id)
        if deleted:
            return {"success": True, "message": "Order deleted successfully"}
        return {"success": False, "message": "Order not found"}
    except Exception as e:
        return {"success": False, "message": str(e)}


@app.get("/api/orders")
async def get_orders():
    try:
        orders = await database.get_all_orders()
        return orders
    except Exception as e:
        return []


@app.get("/api/notifications")
async def get_notifications():
    try:
        notifications = await database.get_all_notifications()
        return notifications
    except Exception as e:
        return []


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)