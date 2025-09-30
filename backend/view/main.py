from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.controller.routers import plane_router  # <- תייבאי לפי השם של הקובץ שלך
from backend.model.db import ping

app = FastAPI(title="Planes Management API")

app.include_router(plane_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/db/ping")
def db_ping():
    return {"db": "ok" if ping() else "fail"}
