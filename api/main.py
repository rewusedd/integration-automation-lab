from fastapi import FastAPI

app = FastAPI(title="Integration Automation Lab API")


@app.get("/health")
def health():
    return {"ok": True}
