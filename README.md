# ✈️ FlySmart – Plane Management System

A modern system for managing planes with **FastAPI (Backend)** and **PySide6 (Frontend)**, designed using **MVC/MVP architecture**.  
Built as a final project for *Windows Systems Engineering*.  

---

## 📊 Badges
![Python](https://img.shields.io/badge/python-3.12-blue.svg?logo=python&logoColor=white)  
![FastAPI](https://img.shields.io/badge/FastAPI-0.116.1-009688?logo=fastapi)  
![PySide6](https://img.shields.io/badge/PySide6-6.9.2-green.svg)  
![License](https://img.shields.io/badge/license-MIT-lightgrey.svg)  

---

## 📦 Installation & Setup

### 1️⃣ Create Virtual Environment
```powershell
.\.venv\Scripts\activate
```

### 2️⃣ Install Dependencies
```powershell
pip install -r requirements.txt
```

---

## 🚀 Run the Project

### ▶ Backend (FastAPI)
```powershell
uvicorn backend.view.main:app --reload --reload-dir backend
```

📍 The API will be available at:  
👉 [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) *(Swagger UI)*  

---

### ▶ Frontend (PySide6 GUI)
Open a new terminal (while backend is running):

```powershell
python -m frontend.main
```

---

## 🗂 Project Structure
```
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
```

---

## ✨ Features
- ✅ Full **CRUD API** for planes  
- ✅ Modern **GUI** with PySide6  
- ✅ Clear **MVC/MVP architecture**  
- ✅ Built-in API docs via **Swagger UI**  
- ✅ SQLAlchemy integration with SQL Server  

---

## 📸 Screenshots

### 🔹 Swagger API
![Swagger Screenshot](docs/screenshots/swagger.png)

### 🔹 PySide6 GUI
![GUI Screenshot](docs/screenshots/gui.png)

*(replace these with actual screenshots of your project)*

---

## 📑 Example API Usage

### ➕ Create Plane (POST `/planes/`)
**Request**
```json
{
  "Name": "Airbus A350",
  "Year": 2021,
  "MadeBy": "Airbus",
  "Picture": "https://example.com/airbus.jpg",
  "NumOfSeats1": 30,
  "NumOfSeats2": 60,
  "NumOfSeats3": 180
}
```

**Response**
```json
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
```

---

✨ With **FlySmart**, you can manage planes through both a clean **REST API** and a beautiful **desktop GUI**.  
