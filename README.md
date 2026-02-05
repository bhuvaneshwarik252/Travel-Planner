# 🌍 FastAPI Travel Planner

A backend-driven **Travel Planner API** built with **FastAPI** that aggregates travel-related data such as **flights, cities, and attractions** from multiple third-party APIs into a unified RESTful service.

This project demonstrates **clean backend architecture**, **secure API integration**, and **modular design**, making it suitable for **real-world applications, learning, and portfolio use**.

---
 
## 📌 Project Overview

The **FastAPI Travel Planner** allows clients to:

* Search flights using external travel APIs
* Look up cities and destinations
* Discover nearby attractions and places
* Store and manage travel-related data locally
* Interact with well-documented REST APIs via Swagger UI

The system follows **industry-standard backend practices**, including routers, services, schemas, and CRUD layers.

---

## 🚀 Features

### ✈️ Flight Search

* Real-time flight data retrieval
* Supports origin, destination, and travel dates
* Integrated with **Amadeus Travel API**

### 🌆 City Search

* City autocomplete and filtering
* Country and region-based lookup
* Powered by **GeoDB Cities API**

### 🗺️ Places & Attractions

* Discover nearby tourist attractions
* Category-based exploration (nature, culture, food, etc.)
* Powered by **OpenTripMap API**

### 💾 Data Persistence

* SQLite database for local storage
* CRUD operations for travel-related data
* SQLAlchemy ORM integration

### 📘 API Documentation

* Auto-generated Swagger UI
* Interactive API testing
* Request/response schema validation

---

## 🧠 Learning Objectives

This project helps you gain hands-on experience with:

* FastAPI project structuring
* RESTful API design
* Third-party API integration
* SQLite database handling
* CRUD operations using SQLAlchemy
* Schema validation using Pydantic
* Secure configuration using environment variables

---

## 🛠️ Tech Stack

### Backend

* **Python**
* **FastAPI**
* **SQLite3**
* **SQLAlchemy**
* **Pydantic**
* **Swagger UI**
* **Uvicorn**

### Frontend (Optional / Minimal)

* **HTML**
* **CSS**
* **Bootstrap**
* **Vanilla JavaScript**

---

## 🔌 External APIs Used

| API                    | Purpose                   |
| ---------------------- | ------------------------- |
| **Amadeus Travel API** | Flight search             |
| **GeoDB Cities API**   | City & destination search |
| **OpenTripMap API**    | Places & attractions      |

---

## 📂 Project Structure

```
crud-app/
├── src/
│   ├── main.py               # Application entry point
│   ├── database.py           # Database connection
│   ├── models.py             # SQLAlchemy models
│   ├── schemas.py            # Pydantic schemas
│   ├── crud.py               # Database CRUD logic
│   │
│   ├── routers/
│   │   ├── users.py          # User management endpoints
│   │   └── travel.py         # Travel search endpoints
│   │
│   ├── services/
│   │   └── travel_service.py # External API integration
│
├── config/
│   └── settings.py           # Environment & app configuration
│
├── db/                       # SQLite database storage
├── .env                      # Environment variables (ignored)
└── README.md
```

---

## 🔁 High-Level Request Flow

```
Client
  ↓
FastAPI Router (routers/)
  ↓
Service Layer (services/)
  ↓
External API / Database
  ↓
Validated Response (schemas)
```

---

## ⚙️ Setup & Installation

### 1️⃣ Clone the Repository

```bash
git clone https://github.com/bhuvaneshwarik252/Travel-Planner.git
cd crud-app
```

---

### 2️⃣ Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate   # Linux / macOS
venv\Scripts\activate      # Windows
```

---

### 3️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

---

### 4️⃣ Configure Environment Variables

Create a `.env` file in the root directory:

```env
DATABASE_URL=sqlite:///./db/crud_db.sqlite
APP_NAME=FastAPI Travel Planner
DEBUG_MODE=True

AMADEUS_CLIENT_ID=your_amadeus_client_id
AMADEUS_CLIENT_SECRET=your_amadeus_client_secret

OPENTRIPMAP_API_KEY=your_opentripmap_api_key

GEODB_API_KEY=your_geodb_api_key
GEODB_API_HOST=wft-geo-db.p.rapidapi.com
```

⚠️ **Do not commit `.env` files**.

---

## ▶️ Running the Application

```bash
uvicorn src.main:app --reload
```

The application will start at:

```
http://localhost:8000
```

---

## 📘 API Documentation (Swagger UI)

Access interactive API docs at:

```
http://localhost:8000/docs
```

Features:

* Endpoint testing
* Request/response schema visualization
* Validation error feedback

---

## 🗄️ Database

* Uses **SQLite** for simplicity
* Stored in the `db/` directory
* Managed using SQLAlchemy ORM

### Example Tables

* users
* trips
* flight_search_history
* saved_destinations

---

## 🧪 Example Use Cases

* Travel search backend for web/mobile apps
* API integration practice project
* FastAPI portfolio project
* Backend service for travel-tech applications

---

## 📌 Future Enhancements

* 🔐 JWT-based authentication
* 👤 User-specific trip management
* 🔔 Flight price alerts
* 🤖 AI-powered destination recommendations
* 📊 Analytics & travel insights
* ☁️ Cloud deployment (AWS / GCP)

---

## 🧑‍💻 Author

**FastAPI Travel Planner**
Built as a backend-focused learning and portfolio project.

---

## 📜 License

This project is licensed under the **MIT License**.
