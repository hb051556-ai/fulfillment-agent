# Order Fulfillment Communication Agent

A complete full-stack order fulfillment system with AI-powered notifications.

## Tech Stack
- **Frontend:** Pure HTML + CSS + JavaScript
- **Backend:** Python + FastAPI
- **Database:** MongoDB
- **AI:** Google Gemini API

## Features
- Place new orders
- Trigger order delay
- Mark order as delivered
- AI-generated notifications (Urdu/English mix)
- Search orders
- Pagination (5 per page)
- Dark/Light mode
- Auto-refresh (15s/10s)
- Manual refresh button

## Installation

1. Install dependencies:
```bash
pip install fastapi uvicorn motor pymongo google-generativeai
```

2. Start MongoDB:
```bash
net start MongoDB
```

3. Setup database:
```bash
python setup_db.py
```

4. Start backend:
```bash
cd backend
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

5. Open frontend:
```
frontend/index.html
```

## API Endpoints
- `GET /api/orders` - Get all orders
- `GET /api/notifications` - Get all notifications
- `POST /api/order` - Create new order
- `POST /api/delay` - Trigger delay
- `POST /api/delivered` - Mark delivered

## Author
- GitHub: hb051556-ai

## License
MIT