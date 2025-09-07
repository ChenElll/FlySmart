from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.db import ping
from app.routers import flights

app = FastAPI(title="FlySmart API")  # <- קודם יוצרים את האובייקט

app.include_router(flights.router)   # <- אחר כך מחברים את הנתיבים

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
