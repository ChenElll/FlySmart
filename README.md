✈️ FlySmart – Plane Management System

A complete system for plane management built with FastAPI (Backend) and PySide6 (Frontend), following the MVC/MVP architecture.

📦 Installation & Setup
1️⃣ Create Virtual Environment
# Activate the virtual environment
.\.venv\Scripts\activate

2️⃣ Install Dependencies
pip install -r requirements.txt

🚀 Run the Project
▶ Backend (FastAPI)
uvicorn backend.view.main:app --reload --reload-dir backend


📍 The API will be available at:
👉 http://127.0.0.1:8000/docs
 (Swagger UI)

▶ Frontend (PySide6 GUI)

Open a new terminal (while backend is running):

python -m frontend.main

🗂 Project Structure
FlySmart/
│── backend/        # Backend (FastAPI + SQLAlchemy)
│   ├── model/      # Models, Schemas, Database
│   ├── controller/ # CRUD logic + Routers
│   └── view/       # main.py (API entry point)
│
│── frontend/       # Frontend (PySide6 GUI)
│   ├── model/      # Entity classes
│   ├── presenter/  # Business logic (API communication)
│   └── view/       # GUI (Table + CRUD controls)
│
│── requirements.txt
│── README.md
│── .env

✨ Features

✅ Full CRUD API for planes

✅ Modern GUI with PySide6

✅ Clear MVC/MVP architecture (clean separation of concerns)

✅ Built-in API docs via Swagger UI

✅ Ready for database integration with SQLAlchemy

📸 Screenshots

🔹 Swagger API
(insert screenshot of /docs)

🔹 PySide6 GUI
(insert screenshot of the GUI table with planes)

📑 Example API Usage
➕ Create Plane (POST /planes/)

Request

{
  "Name": "Airbus A350",
  "Year": 2021,
  "MadeBy": "Airbus",
  "Picture": "https://example.com/airbus.jpg",
  "NumOfSeats1": 30,
  "NumOfSeats2": 60,
  "NumOfSeats3": 180
}


Response

{
  "PlaneId": 1,
  "Name": "Airbus A350",
  "Year": 2021,
  "MadeBy": "Airbus",
  "Picture": "https://example.com/airbus.jpg",
  "NumOfSeats1": 30,
  "NumOfSeats2": 60,
  "NumOfSeats3": 180
}


✨ With FlySmart, you can easily manage planes through both a clean REST API and a beautiful desktop GUI.