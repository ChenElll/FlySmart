from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from controller.routers import router
from model.db import ping

app = FastAPI(title="Flight Management API")

app.include_router(router)

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
