import os
from fastapi import FastAPI, HTTPException, Header
from fastapi.responses import JSONResponse

app = FastAPI(title="Integration Automation Lab API")

DEMO_PARTNER_API_KEY = os.getenv("DEMO_PARTNER_API_KEY", "dev-secret")

@app.get("/demo/partner/orders")
def demo_partner_orders(
    status: str = "new",
    x_api_key: str | None = Header(default=None)
):
    if x_api_key != DEMO_PARTNER_API_KEY:
        raise HTTPException(status_code=401, detail="invalid_api_key")

    raw_orders = [
        {
            "orderId": "ord-1001",
            "customer": {"fullName": "Alice Doe", "email": "alice@example.com"},
            "amount": {"value": 120, "currency": "USD"},
            "meta": {"source": "partner_api", "status": status},
        },
        {
            "orderId": "ord-1002",
            "customer": {"fullName": "Bob Ray", "email": "bob@example.com"},
            "amount": {"value": 80, "currency": "USD"},
            "meta": {"source": "partner_api", "status": status},
        },
    ]

    return {
        "provider": "demo_partner",
        "count": len(raw_orders),
        "orders": raw_orders,
    }