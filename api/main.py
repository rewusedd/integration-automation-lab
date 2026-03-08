from datetime import datetime, timezone
from fastapi import FastAPI, Query

app = FastAPI(title="Integration Automation Lab API")


@app.get("/health")
def health():
    return {"ok": True}


@app.get("/demo/items")
def demo_items(limit: int = Query(default=3, ge=1, le=10)):
    items = [
        {
            "id": f"item-{i}",
            "name": f"demo-item-{i}",
            "price": i * 10,
            "status": "new",
        }
        for i in range(1, limit + 1)
    ]

    return {
        "source": "demo_items",
        "fetched_at": datetime.now(timezone.utc).isoformat(),
        "count": len(items),
        "items": items,
    }
