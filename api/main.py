import os
from datetime import datetime, timezone
from typing import Any, Literal
from uuid import uuid4

import psycopg
from psycopg.types.json import Jsonb
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

app = FastAPI(title="Integration Automation Lab API")

attempt_store: dict[str, int] = {}


def get_db_connection():
    return psycopg.connect(
        host=os.getenv("POSTGRES_HOST", "postgres"),
        port=int(os.getenv("POSTGRES_PORT", "5432")),
        dbname=os.getenv("POSTGRES_DB", "app"),
        user=os.getenv("POSTGRES_USER", "app"),
        password=os.getenv("POSTGRES_PASSWORD", "app"),
        autocommit=False,
    )


@app.get("/health")
def health():
    return {"ok": True}


@app.get("/demo/items")
def demo_items(limit: int = 3):
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


class RetryLabRequest(BaseModel):
    request_key: str = Field(..., min_length=1)
    mode: Literal["success", "flaky_429", "flaky_500", "bad_input"]
    fail_times: int = Field(0, ge=0, le=10)
    attempt: int = Field(1, ge=1)
    payload: dict = Field(default_factory=dict)


class ProcessRequest(BaseModel):
    request_id: str | None = None
    source: str = Field(..., min_length=1)
    event_id: str = Field(..., min_length=1)
    idempotency_key: str | None = None
    trace_metadata: dict[str, Any] = Field(default_factory=dict)
    payload: dict[str, Any] = Field(default_factory=dict)


@app.post("/demo/retry-lab")
def retry_lab(req: RetryLabRequest):
    if req.mode == "bad_input":
        return JSONResponse(
            status_code=400,
            content={
                "ok": False,
                "retryable": False,
                "error_code": "bad_input",
                "message": "Demo permanent error: bad input",
                "request_key": req.request_key,
                "attempt": req.attempt,
            },
        )

    if "name" not in req.payload:
        return JSONResponse(
            status_code=400,
            content={
                "ok": False,
                "retryable": False,
                "error_code": "validation_error",
                "message": "payload.name is required",
                "request_key": req.request_key,
                "attempt": req.attempt,
            },
        )

    key = f"{req.request_key}:{req.mode}"
    current_seen = attempt_store.get(key, 0) + 1
    attempt_store[key] = current_seen

    if req.mode == "flaky_429" and current_seen <= req.fail_times:
        return JSONResponse(
            status_code=429,
            headers={"Retry-After": "2"},
            content={
                "ok": False,
                "retryable": True,
                "error_code": "rate_limited",
                "message": f"429 simulated on internal hit #{current_seen}",
                "request_key": req.request_key,
                "attempt": req.attempt,
                "internal_seen": current_seen,
            },
        )

    if req.mode == "flaky_500" and current_seen <= req.fail_times:
        return JSONResponse(
            status_code=500,
            content={
                "ok": False,
                "retryable": True,
                "error_code": "server_error",
                "message": f"500 simulated on internal hit #{current_seen}",
                "request_key": req.request_key,
                "attempt": req.attempt,
                "internal_seen": current_seen,
            },
        )

    return {
        "ok": True,
        "retryable": False,
        "message": "success",
        "request_key": req.request_key,
        "attempt": req.attempt,
        "internal_seen": current_seen,
        "payload": req.payload,
    }


@app.post("/demo/retry-lab/reset")
def retry_lab_reset():
    attempt_store.clear()
    return {"ok": True, "message": "attempt store cleared"}


@app.post("/process", status_code=202)
def process(req: ProcessRequest):
    request_id = req.request_id or str(uuid4())

    insert_sql = """
    INSERT INTO app.events_inbox (
        request_id,
        source,
        event_id,
        idempotency_key,
        trace_metadata,
        payload,
        status,
        attempts
    )
    VALUES (%s, %s, %s, %s, %s, %s, 'received', 0)
    ON CONFLICT (source, event_id)
    DO NOTHING
    RETURNING id, received_at, status;
    """

    select_existing_sql = """
    SELECT id, request_id, received_at, status
    FROM app.events_inbox
    WHERE source = %s AND event_id = %s;
    """

    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    insert_sql,
                    (
                        request_id,
                        req.source,
                        req.event_id,
                        req.idempotency_key,
                        Jsonb(req.trace_metadata),
                        Jsonb(req.payload),
                    ),
                )
                row = cur.fetchone()

                if row is not None:
                    inbox_id, received_at, status = row
                    conn.commit()
                    return {
                        "ok": True,
                        "message": "event accepted",
                        "request_id": request_id,
                        "inbox_id": inbox_id,
                        "source": req.source,
                        "event_id": req.event_id,
                        "status": status,
                        "received_at": received_at.isoformat(),
                        "duplicate": False,
                    }

                cur.execute(select_existing_sql, (req.source, req.event_id))
                existing = cur.fetchone()
                conn.commit()

                if existing is None:
                    raise HTTPException(
                        status_code=500,
                        detail="inbox conflict detected but existing row not found",
                    )

                inbox_id, existing_request_id, received_at, status = existing
                return JSONResponse(
                    status_code=200,
                    content={
                        "ok": True,
                        "message": "duplicate delivery acknowledged",
                        "request_id": existing_request_id,
                        "inbox_id": inbox_id,
                        "source": req.source,
                        "event_id": req.event_id,
                        "status": status,
                        "received_at": received_at.isoformat(),
                        "duplicate": True,
                    },
                )

    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"db_write_failed: {exc}")