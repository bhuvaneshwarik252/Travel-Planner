# Implementation Plan - Geoapify Integration

The goal is to integrate **Geoapify** as a service to fetch tourist attractions and city data, providing a robust alternative to the current OpenTripMap and GeoDB implementations.

## User Review Required
> [!IMPORTANT]
> **API Key**: You provided the API Key `cd757b50e3154460ab7c972693e9e02c`. This will be added to your `.env` file. Do not commit this file to version control.

## Proposed Changes

### Configuration
#### [MODIFY] [settings.py](file:///home/vk-linux/Desktop/bhuvi-project/Travel-Planner/crud-app/config/settings.py)
- Add `GEOAPIFY_API_KEY` to the settings schema.

### New Service
#### [NEW] [geoapify_service.py](file:///home/vk-linux/Desktop/bhuvi-project/Travel-Planner/crud-app/src/services/geoapify_service.py)
- Implement `GeoapifyService` class.
- Method `get_places(lat, lon, categories, radius)`: To fetch tourist attractions.
- Method `forward_geocoding(text)`: To find coordinates for a city/location.

### Routers
#### [MODIFY] [travel.py](file:///home/vk-linux/Desktop/bhuvi-project/Travel-Planner/crud-app/src/routers/travel.py)
- Update `/api/travel/geoapify/places` to accept:
    - `city`: Optional string.
    - `lat` / `lon`: Optional floats.
- Logic:
    - If `city` is provided, call `geoapify_service.forward_geocoding(city)` to get coordinates.
    - Use coordinates to call `get_places`.
    - Functionality covers "Current Location" (client sends lat/lon) and "Map Choice" (client sends selected lat/lon).

### Environment
#### [MODIFY] [.env](file:///home/vk-linux/Desktop/bhuvi-project/Travel-Planner/crud-app/.env)
- Add `GEOAPIFY_API_KEY=cd757b50e3154460ab7c972693e9e02c`.

## Verification Plan
### Automated Tests
- Run the server and call the new endpoints using `curl` or the browser.

### Manual Verification
1. **Service Check**: Verify `GeoapifyService` can connect and fetch data.
2. **Attraction Search**: Search for attractions near a known city (e.g., Paris) and verify results contain names, categories, and locations.
3. **Swagger UI**: Check that the new endpoints appear in `/docs`.
