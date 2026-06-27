# Weather Station

A full-stack weather app built for the PM Accelerator AI Engineer Intern technical assessment (both Tech Assessment #1 and #2).

Built by **[YOUR NAME HERE]**.

## What this is

- **Frontend** (`/frontend`): React + Vite. Lets you look up the weather for any location (or your current GPS position), see current conditions and a 5-day forecast, and manage a persistent "logbook" of saved location + date-range lookups.
- **Backend** (`/backend`): Python + FastAPI + SQLite. Resolves locations, fetches weather data from [Open-Meteo](https://open-meteo.com) (free, no API key needed), and provides full CRUD over saved records plus multi-format data export.

No API keys are required anywhere in this project — everything runs out of the box.

## Quick start

### 1. Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env            # optional: add an API key here to enable AI summaries
uvicorn app.main:app --reload
```

The API is now running at `http://localhost:8000`. Interactive docs (Swagger UI) are at `http://localhost:8000/docs`. A `weather_app.db` SQLite file is created automatically on first run — no setup needed.

### 2. Frontend

In a second terminal:

```bash
cd frontend
npm install
cp .env.example .env   # defaults to http://localhost:8000, change if needed
npm run dev
```

Open the URL it prints (typically `http://localhost:5173`).

## How it maps to the assessment requirements

### Tech Assessment #1 (Frontend)
- Location entry by free text (city, zip/postal code, landmark, etc.) — resolved server-side via geocoding, with fuzzy matching.
- "Use my location" button using the browser Geolocation API.
- Current weather shown with an icon, temperature, "feels like," humidity, wind, and an air-quality badge.
- **5-day forecast** (`1.1`): horizontal forecast strip *and* a trend chart (high/low temps + rain chance) built with Recharts.
- **Error handling** (`1.2`): a dismissible error banner for "location not found," failed requests, and denied geolocation permission, plus a no-backend-running fallback message.
- Built in React (JS framework, no Python/Java), responsive down to mobile via CSS grid/flexbox + media queries.
- Dark mode toggle (persisted across visits).
- **Home vs. destination comparison**: an expandable panel where you enter two locations (or use your current location for "Home") and get a side-by-side weather view plus a plain-language summary of how they differ — directly implements the assessment's own framing of "weather where I am vs. somewhere I'm traveling to." (`frontend/src/components/CompareLocations.jsx`, comparison logic in `frontend/src/lib/comparison.js`)
- Rule-based "things to consider" tips (umbrella, hydration, air quality, etc.) generated from the weather data — directly answers the assessment's prompt about non-obvious considerations.
- Optional AI-generated weather summary (see below) — only appears if you configure an API key; otherwise the app behaves identically.

### Tech Assessment #2 (Backend)
- **CRUD** (`2.1`) over a SQLite database via `/api/records`:
  - `POST /api/records` — **Create**: location + date range → validated (date order, max forecast horizon) and geocoded (fuzzy-matched, 404 if not found) → fetches and stores daily temperatures for the range.
  - `GET /api/records`, `GET /api/records/{id}` — **Read**: all saved records, with no per-user segmentation (per the assessment spec).
  - `PUT /api/records/{id}` — **Update**: notes are always editable; changing location or dates re-validates and re-fetches the data.
  - `DELETE /api/records/{id}` — **Delete**.
- **API integration stand-apart** (`2.2`): an additional Open-Meteo **Air Quality API** call (US AQI, PM2.5, PM10) surfaced alongside current weather.
- **Data export** (`2.3`): `GET /api/records/{id}/export?format=...` and `GET /api/records/export/all?format=...`, supporting **JSON, CSV, XML, Markdown, and PDF**.

### Combining historical + forecast data for a date range
Open-Meteo splits "recent past + future" from "deep history" across two different endpoints. `app/services/weather.py` hides that seam: it picks the Forecast API (covers ~92 days back to 16 days ahead) and/or the Archive API (anything older) as needed for the requested range, and merges the results into one continuous daily series.

### Optional AI weather summary
`backend/app/services/ai_insights.py` will generate a short natural-language summary of the current weather and forecast, but **only if** you set `ANTHROPIC_API_KEY` or `OPENAI_API_KEY` in `backend/.env` (copy `backend/.env.example` to get started). With no key configured, this feature is silently disabled — the rest of the app is completely unaffected. If a key is set but the call fails (bad key, rate limit, no internet), it also fails silently rather than breaking the weather lookup. This is intentional: a "nice to have" AI feature should never be a point of failure for the core app.

## Project structure

```
backend/
  app/
    main.py              # FastAPI app, CORS, root + /api/about
    database.py           # SQLAlchemy engine/session (SQLite)
    models.py              # WeatherRecord, DailyTemperature ORM models
    schemas.py             # Pydantic request/response models
    routers/
      weather.py           # stateless current/forecast lookups
      records.py           # CRUD + export endpoints
    services/
      geocoding.py          # Open-Meteo Geocoding API wrapper
      weather.py            # Open-Meteo Forecast + Archive API wrapper
      air_quality.py        # Open-Meteo Air Quality API wrapper
      recommendations.py    # rule-based "things to consider" tips
      ai_insights.py        # optional AI summary (no-op without an API key)
      export.py             # JSON/CSV/XML/Markdown/PDF export
      weather_codes.py       # WMO weather code -> description map
  requirements.txt
  .env.example              # optional AI API keys go here
frontend/
  src/
    App.jsx                # top-level state + data flow
    lib/api.js              # fetch wrapper for the backend
    components/             # SearchBar, CurrentWeatherCard, ForecastStrip,
                             # ForecastChart, RecommendationsList, AiInsightCard,
                             # ThemeToggle, LogbookSection/LogbookRecord, etc.
    index.css, styles.css   # design tokens (incl. dark theme) + component styles
```

## Tech stack

- **Backend**: Python, FastAPI, SQLAlchemy, SQLite, httpx, fpdf2
- **Frontend**: React, Vite, plain CSS (no UI framework)
- **External APIs**: Open-Meteo Geocoding, Forecast, Archive, and Air Quality APIs (all free, keyless)


## Notes

- This was developed and tested with the actual Open-Meteo APIs mocked in automated tests (CRUD flow, validation, and error handling all verified). Live network calls to Open-Meteo will work normally once you run this on a machine with standard internet access.
- Row-level security / per-user segmentation was intentionally **not** implemented, per the assessment spec ("Row level security is not necessary").
