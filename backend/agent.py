import os
import google.generativeai as genai
import database

genai.configure(api_key="AIzaSyDhQ4nzfYSdpOqJDYam0hrbRXzfFKRUCzQ")
model = genai.GenerativeModel('gemini-2.0-flash')


# ============== ORDER AGENT ==============
async def create_order(order_id: str, customer: str, sku: str, address: str, channel: str, sla: str, eta: str):
    order_data = {
        "order_id": order_id,
        "customer_name": customer,
        "sku": sku,
        "address": address,
        "channel": channel,
        "sla": sla,
        "status": "confirmed",
        "eta": eta
    }
    await database.insert_order(order_data)
    return f"Order {order_id} created successfully"


# ============== NOTIFICATION AGENT ==============
async def generate_message(customer: str, channel: str, status: str, eta: str = None):
    prompts = {
        "confirmed": f"Write order confirmation message for {customer}. Channel: {channel}. Include ETA: {eta}. WhatsApp: friendly Urdu/English, SMS: short, Email: formal.",
        "delayed": f"Write order delay message for {customer}. Channel: {channel}. New ETA: {eta}. WhatsApp: friendly Urdu/English, SMS: short, Email: formal.",
        "delivered": f"Write order delivery message for {customer}. Channel: {channel}. WhatsApp: friendly Urdu/English, SMS: short, Email: formal."
    }
    try:
        response = model.generate_content(prompts[status])
        return response.text
    except:
        return f"Your order has been {status}"


async def send_notification(customer_name: str, channel: str, message: str, order_id: str):
    count = await database.get_notification_count(order_id)
    if count >= 4:
        return "MAX LIMIT REACHED - Cannot send more notifications"
    
    notification_data = {
        "order_id": order_id,
        "customer": customer_name,
        "channel": channel,
        "message": message
    }
    await database.insert_notification(notification_data)
    
    log_data = {
        "order_id": order_id,
        "event": "notification_sent",
        "channel": channel,
        "message": message
    }
    await database.insert_log(log_data)
    
    await database.update_order(order_id, {"notification_count": count + 1})
    
    return f"Notification sent via {channel} to {customer_name}"


# ============== STATUS AGENT ==============
async def update_order_status(order_id: str, status: str, new_eta: str):
    update_data = {"status": status}
    if new_eta:
        update_data["eta"] = new_eta
    
    await database.update_order(order_id, update_data)
    
    log_data = {
        "order_id": order_id,
        "event": "status_updated",
        "status": status,
        "new_eta": new_eta
    }
    await database.insert_log(log_data)
    
    return f"Order {order_id} status updated to {status}"


# ============== RUNNER FUNCTIONS ==============
async def run_order_agent(order_id: str, customer: str, sku: str, address: str, channel: str, sla: str, eta: str):
    result = await create_order(order_id, customer, sku, address, channel, sla, eta)
    return f"Order Agent: {result}"


async def run_notification_agent(order_id: str, customer: str, channel: str, status: str, eta: str = None):
    message = await generate_message(customer, channel, status, eta)
    result = await send_notification(customer, channel, message, order_id)
    return f"Notification Agent: {result}"


async def run_status_agent(order_id: str, customer: str, channel: str, status: str, new_eta: str):
    status_result = await update_order_status(order_id, status, new_eta)
    message = await generate_message(customer, channel, status, new_eta)
    notif_result = await send_notification(customer, channel, message, order_id)
    return f"Status Agent: {status_result} | {notif_result}"


# ============== MAIN ORCHESTRATOR ==============
async def run_orchestrator(task: str, **kwargs):
    """
    Multi-Agent Orchestrator
    Routes tasks to appropriate agent
    """
    task = task.lower()
    
    if "create" in task or "place" in task:
        return await run_order_agent(
            kwargs.get("order_id"),
            kwargs.get("customer"),
            kwargs.get("sku"),
            kwargs.get("address"),
            kwargs.get("channel"),
            kwargs.get("sla"),
            kwargs.get("eta")
        )
    
    elif "delay" in task:
        return await run_status_agent(
            kwargs.get("order_id"),
            kwargs.get("customer"),
            kwargs.get("channel"),
            "delayed",
            kwargs.get("new_eta")
        )
    
    elif "deliver" in task:
        return await run_status_agent(
            kwargs.get("order_id"),
            kwargs.get("customer"),
            kwargs.get("channel"),
            "delivered",
            None
        )
    
    elif "confirm" in task:
        return await run_notification_agent(
            kwargs.get("order_id"),
            kwargs.get("customer"),
            kwargs.get("channel"),
            "confirmed",
            kwargs.get("eta")
        )
    
    else:
        return "Unknown task - I can handle: create order, delay order, deliver order, confirm order"