from fastapi import FastAPI

app = FastAPI(title="orders-api")


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "service": "orders-api"}


@app.get("/")
def root() -> dict:
    return {"service": "orders-api", "owner": "platform-team"}
