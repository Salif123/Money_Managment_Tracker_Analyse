import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from config import settings, upload_path
from routers import health, invoices

app = FastAPI(
    title="Bill Manager API",
    description="Backend API for local Bill Manager application",
    version="1.0.0"
)

# CORS Configuration
origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers. Mount health and invoices under /api
app.include_router(health.router, prefix="/api")
app.include_router(invoices.router, prefix="/api")

# Mount upload directory to serve files statically
app.mount("/uploads", StaticFiles(directory=upload_path), name="uploads")

@app.get("/")
def read_root():
    return {
        "message": "Bill Manager API is running.",
        "health_check": "/api/health"
    }
