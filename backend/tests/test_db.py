import os, pyodbc
from dotenv import load_dotenv

load_dotenv()

conn_str = (
    f"DRIVER={{{os.getenv('ODBC_DRIVER')}}};"
    f"SERVER={os.getenv('DB_SERVER')};"
    f"DATABASE={os.getenv('DB_NAME')};"
    f"UID={os.getenv('DB_USER')};"
    f"PWD={os.getenv('DB_PASSWORD')};"
    f"TrustServerCertificate=Yes;"
)

print("🔄 מנסה להתחבר ל-Somee...")
with pyodbc.connect(conn_str, timeout=10) as conn:
    cursor = conn.cursor()
    cursor.execute("SELECT SUSER_SNAME(), DB_NAME(), GETDATE()")
    row = cursor.fetchone()
    print("✅ התחברת בהצלחה!")
    print(f"משתמש: {row[0]} | דאטאבייס: {row[1]} | תאריך שרת: {row[2]}")
