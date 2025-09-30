import os
from urllib.parse import quote_plus
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

load_dotenv()

server   = os.getenv("DB_SERVER")
print()
db       = os.getenv("DB_NAME")
user     = os.getenv("DB_USER")
password = quote_plus(os.getenv("DB_PASSWORD", ""))
driver   = quote_plus(os.getenv("ODBC_DRIVER", "ODBC Driver 17 for SQL Server"))
trust    = "yes" if os.getenv("TRUST_CERT","yes").lower() in ("1","true","yes") else "no"

SQLALCHEMY_DATABASE_URI = (
    f"mssql+pyodbc://{user}:{password}@{server}/{db}"
    f"?driver={driver}&TrustServerCertificate={trust}"
)

engine = create_engine(
    SQLALCHEMY_DATABASE_URI,
    echo=False,
    pool_pre_ping=True,
    future=True,
)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)

def ping():
    with engine.connect() as conn:
        return conn.execute(text("SELECT 1")).scalar() == 1
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
