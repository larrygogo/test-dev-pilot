"""test-dev-pilot: FastAPI 示例应用"""
from fastapi import FastAPI

app = FastAPI(title="test-dev-pilot", version="0.1.0")


@app.get("/")
async def root():
    return {"message": "Hello, test-dev-pilot!"}


@app.get("/health")
async def health():
    return {"status": "ok"}
