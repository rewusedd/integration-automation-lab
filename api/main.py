from datetime import datetime, timezone
from fastapi import FastAPI, Query

app = FastAPI(title="Integration Automation Lab API")


@app.get("/health")
def health():
    return {"ok": True}


@app.get("/demo/items")
def demo_items(
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=2, ge=1, le=5),
):
    all_items = [
        {
            "id": f"item-{i}",
            "name": f"demo-item-{i}",
            "price": i * 10,
            "status": "new" if i % 2 else "processed",
        }
        for i in range(1, 8)
    ]

    total_items = len(all_items)
    total_pages = (total_items + limit - 1) // limit

    start_idx = (page - 1) * limit
    end_idx = start_idx + limit

    items = all_items[start_idx:end_idx]

    has_more = page < total_pages
    next_page = page + 1 if has_more else None

    return {
        "source": "demo_items",
        "fetched_at": datetime.now(timezone.utc).isoformat(),
        "page": page,
        "limit": limit,
        "count": len(items),
        "total_items": total_items,
        "total_pages": total_pages,
        "has_more": has_more,
        "next_page": next_page,
        "items": items,
    }