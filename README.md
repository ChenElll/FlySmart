# ✈️ FlySmart – Backend API

This is the backend for the FlySmart flight management system, built with **FastAPI** and connected to a **SQL Server database hosted on Somee.com**.

---

## ✅ Prerequisites

Make sure the following are installed on your machine:

- [Python 3.11+](https://www.python.org/downloads/)
- [Git](https://git-scm.com/downloads)
- [Microsoft ODBC Driver 17 for SQL Server](https://learn.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server)

---

## 🚀 Getting Started (Local Development)

### 1. Clone the project
```bash
git clone <your-repo-url>
cd FlySmart/backend
2. Create virtual environment
bash
Copy code
python -m venv .venv
3. Activate the virtual environment
Windows (PowerShell):
bash
Copy code
.venv\Scripts\Activate.ps1
If activation fails, run:

bash
Copy code
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
Then try activating again.

4. Install dependencies
If you have a requirements.txt file:

bash
Copy code
pip install -r requirements.txt
Otherwise, install manually:

bash
Copy code
pip install fastapi uvicorn sqlalchemy pyodbc python-dotenv
5. Create a .env file
Create a file named .env inside the backend/ folder (same folder as main.py) and fill in:

ini
Copy code
DB_SERVER=airlinedb.mssql.somee.com
DB_NAME=airlinedb
DB_USER=Hen_SQLLogin_2
DB_PASSWORD=your_password_here
ODBC_DRIVER=ODBC Driver 17 for SQL Server
TRUST_CERT=yes
Make sure to replace your_password_here with your actual Somee DB password.

6. Run the server
bash
Copy code
uvicorn app.main:app --reload --port 8000
7. Open Swagger (API Docs)
Go to:
http://localhost:8000/docs

You should see a full interactive API interface.

🧪 Example Endpoints to Test
GET /flights → List all flights

POST /flights → Create a new flight

PUT /flights/{flight_id} → Update a flight

DELETE /flights/{flight_id} → Delete a flight

GET /db/ping → Check DB connection

🛠 Technologies Used
FastAPI

SQLAlchemy

pyodbc

Uvicorn

dotenv

SQL Server on somee.com

📁 Project Structure
css
Copy code
backend/
├── app/
│   ├── main.py
│   ├── db.py
│   ├── crud.py
│   ├── models.py
│   ├── schemas.py
│   └── routers.py
📌 Notes
The project connects to an external SQL Server hosted on somee.com.

All API endpoints are documented via Swagger UI.

