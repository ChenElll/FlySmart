import os
from urllib.parse import quote_plus
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# ------------------------------------------------------------
# Load environment variables from the .env file
# (Used to keep database credentials secure and configurable)
# ------------------------------------------------------------
load_dotenv()

# ------------------------------------------------------------
# Read database connection settings from environment variables
# ------------------------------------------------------------
server   = os.getenv("DB_SERVER")
db       = os.getenv("DB_NAME")
user     = os.getenv("DB_USER")
password = quote_plus(os.getenv("DB_PASSWORD", ""))  # URL-safe encoding
driver   = quote_plus(os.getenv("ODBC_DRIVER", "ODBC Driver 17 for SQL Server"))
trust    = "yes" if os.getenv("TRUST_CERT", "yes").lower() in ("1", "true", "yes") else "no"

# ------------------------------------------------------------
# Build the SQLAlchemy connection URI for SQL Server using pyodbc
# Example:
# mssql+pyodbc://user:password@server/db_name?driver=ODBC+Driver+17+for+SQL+Server
# ------------------------------------------------------------
SQLALCHEMY_DATABASE_URI = (
    f"mssql+pyodbc://{user}:{password}@{server}/{db}"
    f"?driver={driver}&TrustServerCertificate={trust}"
)

# ------------------------------------------------------------
# Create the SQLAlchemy Engine
# - The 'engine' is the core interface to the database
# - 'pool_pre_ping=True' ensures broken connections are recycled automatically
# - 'future=True' enables SQLAlchemy 2.0 style behavior
# ------------------------------------------------------------
engine = create_engine(
    SQLALCHEMY_DATABASE_URI,
    echo=False,           # Set to True for SQL debugging
    pool_pre_ping=True,   # Check connections before using them
    future=True,
)

# ------------------------------------------------------------
# Create a factory for new database sessions
# - Each FastAPI request gets its own Session
# - Sessions handle transactions (commit/rollback)
# ------------------------------------------------------------
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)

# ------------------------------------------------------------
# Simple health check for database connection
# Used in /health endpoints or initial startup tests
# ------------------------------------------------------------
def ping():
    with engine.connect() as conn:
        return conn.execute(text("SELECT 1")).scalar() == 1

# ------------------------------------------------------------
# Dependency function for FastAPI
# - Yields a database session for the duration of the request
# - Ensures that the session is properly closed after use
# ------------------------------------------------------------
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
