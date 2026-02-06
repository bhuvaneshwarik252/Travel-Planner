# Travel Planner API Documentation

## 1. External APIs (Consumed)

The application integrates with the following third-party services to fetch travel data:

| API Name | Purpose | Status | Service File |
|----------|---------|--------|--------------|
| **Geoapify** | **Primary Source.** Geocoding, Places/Attractions, and Routing. | ✅ Active (Planner) | `src/services/geoapify_service.py` |
| **Amadeus Travel API** | Flight search and airport data. | ✅ Active (Planner) | `src/services/travel_service.py` |
| **GeoDB Cities API** | City demographics and details (Standalone only). | ⚠️ Standalone | `src/services/geodb_service.py` |
| **OpenTripMap API** | Tourist attractions (Legacy/Standalone). | ⚠️ Standalone | `src/services/opentripmap_service.py` |
| **Unsplash API** | Fallback for high-quality attraction images. | ✅ Active (Fallback) | `src/services/geoapify_service.py` |

---

## 2. Internal API Endpoints

### 2.1 🌍 Intelligent Travel Planner (`/api/plan`)

Aggregates data from Geoapify and Amadeus to build a complete, day-by-day trip plan.

*   **GET** `/api/plan` - **Get Travel Plan**
    *   **Parameters**:
        *   `destination` (required): Single city or comma-separated list (e.g., "Paris" or "Chengannur, Guruvayur").
        *   `origin` (optional): Starting city/airport code (e.g., "London").
        *   `days` (required): Total duration of the trip.
        *   `travel_mode`: `flight`, `train`, `car`, or `bus`.
    *   **Key Features**:
        *   **Multi-Destination**: Automatically sequences multiple cities into a road trip.
        *   **Smart Routing**: Calculates real-time travel (Walk/Transit/Drive) between attractions.
        *   **Budget (INR)**: Estimates costs in Indian Rupees.
        *   **End-to-End**: Includes departure, inter-city travel, and return journey.

### 2.2 ✈️ Travel Data Tools (`/api/travel`)

Direct access to specific travel data services (some use legacy providers).

*   **GET** `/api/travel/geoapify/places` - **Get Places (Geoapify)**
    *   Find attractions by coordinates or city name.
*   **GET** `/api/travel/flights` - **Search Flights**
    *   Real-time flight offers via Amadeus.
*   **GET** `/api/travel/locations` - **Search Locations**
    *   Find airports and cities (Amadeus).
*   **GET** `/api/travel/cities/search` - **Find Cities**
    *   Search by prefix (GeoDB).
*   **GET** `/api/travel/attractions` - **Get Attractions**
    *   Get POIs (OpenTripMap).

### 2.3 👤 User Management (`/api/users`)

Basic CRUD operations for users.

*   **POST** `/api/users` - Create User
*   **GET** `/api/users` - Read Users (List)
*   **GET** `/api/users/{user_id}` - Read Single User
*   **PUT** `/api/users/{user_id}` - Update User
*   **DELETE** `/api/users/{user_id}` - Delete User

### 2.4 🏥 Health Checks (`/health`)

*   **GET** `/health/apis` - **Check External APIs Status**
