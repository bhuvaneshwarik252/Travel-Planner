# FastAPI Travel Planner

## Project Overview

This is a **Backend Application** built with **FastAPI**. It started as a simple CRUD app and has evolved into a **Travel Planner** integrating the **Amadeus API**.

It features:
- **FastAPI** for high-performance API endpoints.
- **SQLAlchemy + SQLite** for local user management.
- **Amadeus SDK** for real-time flight and location searches.
- **Clean Architecture** with separation of concerns (`routers`, `services`, `schemas`).

## Project Structure

```bash
crud-app/
├── src/
│   ├── main.py              # Application entry
│   ├── database.py          # Database connection
│   ├── models.py            # User models
│   ├── schemas.py           # Pydantic schemas
│   ├── crud.py              # DB logic
│   ├── routers/             # API Routers
│   │   ├── users.py         # User management
│   │   └── travel.py        # Travel search endpoints
│   ├── services/
│   │   └── travel_service.py # Amadeus integration
│
├── config/
│   └── settings.py          # Configuration
├── db/                      # Database storage
├── .env                     # API Keys & Config
└── README.md
```

## Setup & Installation

1.  **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

2.  **Configuration**:
    - Rename `.env.example` to `.env` (if applicable) or edit `.env`.
    - **CRITICAL**: You must add your Amadeus API keys to `.env`:
      ```properties
      AMADEUS_CLIENT_ID=your_client_id
      AMADEUS_CLIENT_SECRET=your_client_secret
      ```
    - Get keys from [Amadeus for Developers](https://developers.amadeus.com/).

3.  **Run the Server**:
    ```bash
    uvicorn src.main:app --reload
    ```

## API Endpoints

See the live documentation at `http://localhost:8000/docs`.

### Travel
- `GET /api/travel/locations?keyword=PAR`: Search for cities/airports (e.g., Paris).
- `GET /api/travel/flights?origin=LHR&destination=JFK&departure_date=2024-12-25`: Search for flights.

### Users (CRUD)
- `POST /api/users`: Create user.
- `GET /api/users`: List users.
