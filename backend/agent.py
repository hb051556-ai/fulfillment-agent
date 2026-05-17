import os
import google.generativeai as genai
import database

genai.configure(api_key="AIzaSyDhQ4nzfYSdpOqJDYam0hrbRXzfFKRUCzQ")

model = genai.GenerativeModel('gemini-2.0-flash')


async def generate_message(customer: str, channel: str, status: str, eta: str = None):
    prompts = {
        "confirmed": f"Write a short order confirmation message for customer {customer}. Channel: {channel}. If WhatsApp use friendly Urdu/English mix, if SMS keep short, if email keep formal. Include ETA: {eta}",
        "delayed": f"Write a short order delay message for customer {customer}. Channel: {channel}. New ETA: {eta}. If WhatsApp use friendly Urdu/English mix, if SMS keep short, if email keep formal.",
        "delivered": f"Write a short order delivery message for customer {customer}. Channel: {channel}. If WhatsApp use friendly Urdu/English mix, if SMS keep short, if email keep formal."
    }
    
    try:
        response = model.generate_content(prompts[status])
        return response.text
    except Exception as e:
        return f"Order {status} for {customer}"


async def send_notification(customer_name: str, channel: str, message: str, order_id: str):
    count = await database.get_notification_count(order_id)
    if count >= 4:
        return "MAX LIMIT REACHED"
    
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


async def run_order_confirmed(order_id: str, customer: str, channel: str, eta: str):
    message = await generate_message(customer, channel, "confirmed", eta)
    await update_order_status(order_id, "confirmed", eta)
    await send_notification(customer, channel, message, order_id)
    return f"Order {order_id} confirmed, notification sent"


async def run_order_delayed(order_id: str, customer: str, channel: str, new_eta: str):
    message = await generate_message(customer, channel, "delayed", new_eta)
    await update_order_status(order_id, "delayed", new_eta)
    await send_notification(customer, channel, message, order_id)
    return f"Order {order_id} delayed, notification sent"


async def run_order_delivered(order_id: str, customer: str, channel: str):
    message = await generate_message(customer, channel, "delivered")
    await update_order_status(order_id, "delivered", None)
    await send_notification(customer, channel, message, order_id)
    return f"Order {order_id} delivered, notification sent"