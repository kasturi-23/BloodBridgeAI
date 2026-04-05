<<<<<<< HEAD
# BloodBridge

AI-Powered Emergency Blood Donor Coordination System

## Quick Start

### Option A: Docker Compose (recommended)

```bash
cd bloodbridge
docker-compose up --build
```

- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

### Option B: Run locally

**Backend**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Start PostgreSQL (or use Docker just for DB)
docker run -d -p 5432:5432 -e POSTGRES_PASSWORD=password -e POSTGRES_DB=bloodbridge postgres:16-alpine

# Edit .env with your settings, then:
uvicorn app.main:app --reload
```

**Frontend**
```bash
cd frontend
npm install
npm run dev
```

## Architecture

```
bloodbridge/
├── backend/
│   └── app/
│       ├── agents/
│       │   ├── matching_agent.py       # Agent 1: Find compatible donors
│       │   ├── eligibility_agent.py    # Agent 2: Filter ineligible donors
│       │   └── call_assistant_agent.py # Agent 3: Contact donors, collect ETA
│       ├── models/          # SQLAlchemy database models
│       ├── schemas/         # Pydantic request/response schemas
│       ├── routers/         # FastAPI route handlers
│       ├── services/        # Twilio voice + SMS services
│       ├── seed_data.py     # 10 mock donors for dev
│       └── main.py          # App entry point
└── frontend/
    └── src/
        ├── pages/
        │   ├── Home.jsx             # Request overview dashboard
        │   ├── NewRequest.jsx       # Create blood request form
        │   ├── RequestDashboard.jsx # Live per-request tracking
        │   └── Donors.jsx           # Donor registry management
        ├── components/
        │   ├── DonorCard.jsx        # Donor status card with simulate buttons
        │   ├── StatusBadge.jsx      # Color-coded status labels
        │   └── Navbar.jsx
        └── services/api.js          # Axios API client
```

## Three AI Agents

| Agent | What it does |
|-------|-------------|
| **Matching Agent** | Finds blood-compatible donors within radius, scores by distance + response history |
| **Eligibility Agent** | Filters out donors ineligible today (too-recent donation, medication flag, deferral, etc.) |
| **Call Assistant Agent** | Orchestrates outbound calls via Twilio, captures ETA, sends SMS map directions |

## Dev Mode (No Twilio/API keys needed)

Run without any external API keys. In dev mode:
- Calls are logged but not placed (mock Twilio)
- SMS directions are logged to console
- Use the **Simulate** buttons on each donor card to manually trigger accept/decline/no-answer outcomes

## API Endpoints

| Method | Path | Purpose |
|--------|------|---------|
| POST | `/api/requests/` | Create blood request |
| GET | `/api/requests/` | List all requests |
| GET | `/api/dashboard/{id}` | Live dashboard data |
| POST | `/api/call/start/{id}` | Start donor outreach |
| POST | `/api/call/simulate/{id}` | Simulate call outcome (dev) |
| GET | `/api/donors/` | List donors |
| POST | `/api/donors/` | Add donor |
| POST | `/api/location/consent` | Store location from donor |

Full interactive docs at: http://localhost:8000/docs

## Environment Variables

See `backend/.env.example` for all settings. Minimum required for dev:
```
DATABASE_URL=postgresql://postgres:password@localhost:5432/bloodbridge
```

Add Twilio credentials to enable real voice calls and SMS.
=======
# Blood Donor Matching System

A full-stack hackathon prototype for emergency blood donor coordination. The system uses deterministic donor filtering/ranking and AI-assisted communication summaries.

## Project Overview

Hospitals and blood banks can create urgent blood requests and instantly get ranked donor matches based on:
- blood compatibility
- eligibility and screening status
- donation recency
- geographic distance
- availability and historical response behavior

The platform also generates outreach messages and matching summaries using OpenAI (backend-only).

## Features

- Dashboard with live metrics and urgent alerts
- Blood request creation workflow
- Rule-based donor matching + weighted ranking
- Donor management with filters and status actions
- Donor detail profiles
- Match results with recommendation tags
- Notification center with AI-generated SMS/email drafts
- Simulated notification send + database logging
- Analytics with chart-ready datasets and trend visuals
- MongoDB seed script with realistic mock donor data

## Tech Stack

- Frontend: React, Vite, Tailwind CSS, React Router, Axios, Recharts
- Backend: FastAPI, Pydantic, Uvicorn, Motor (MongoDB async driver)
- Database: MongoDB
- AI: OpenAI API (backend only)

## Folder Structure

```text
backend/
  app/
    main.py
    config.py
    database.py
    routes/
      donors.py
      requests.py
      notifications.py
      analytics.py
    services/
      matching.py
      ai_service.py
    schemas/
      donor.py
      blood_request.py
      notification.py
    utils/
      blood_compatibility.py
      geo.py
      serializers.py
  requirements.txt
  seed_data.py
  .env.example

frontend/
  src/
    components/
    pages/
    services/
    utils/
    App.jsx
    main.jsx
  package.json
  .env.example
```

## Architecture (High Level)

1. Hospital submits request from frontend.
2. FastAPI stores request in MongoDB.
3. Matching service performs deterministic filtering:
   - compatibility by ABO/Rh map
   - eligibility_status = eligible
   - health_screening_status = passed
   - availability_status = available
   - age range check
   - last donation date safety window
4. Matching service ranks candidates with weighted scoring.
5. AI service generates optional summary + outreach draft.
6. Frontend renders ranked matches, notifications, and analytics.

## Rule-Based vs AI Responsibilities

### Rule-Based Matching (Deterministic)
- donor compatibility checks
- eligibility filtering
- availability/screening checks
- ranking score computation
- search radius fallback expansion

### AI-Assisted Functions
- donor outreach message generation (SMS/email)
- match result natural-language summary
- explanation-style communication support

AI does **not** decide medical eligibility or compatibility.

## Setup

## 1) Backend

```bash
cd backend
python -m venv .venv
# Windows
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
```

Set `OPENAI_API_KEY` in `backend/.env` if you want live AI output.

Run API:

```bash
uvicorn app.main:app --reload --port 8000
```

Seed database:

```bash
python seed_data.py
```

## 2) Frontend

```bash
cd frontend
npm install
copy .env.example .env
npm run dev
```

Frontend runs on `http://localhost:5173`.

## Environment Variables

### backend/.env

```env
MONGO_URI=mongodb://localhost:27017
MONGO_DB_NAME=blood_donor_system
OPENAI_API_KEY=your_openai_key
OPENAI_MODEL=gpt-4o-mini
FRONTEND_ORIGIN=http://localhost:5173
```

### frontend/.env

```env
VITE_API_BASE_URL=http://localhost:8000
```

## Core API Endpoints

- `POST /requests`
- `GET /requests`
- `GET /requests/{id}`
- `GET /requests/{id}/matches`
- `GET /donors`
- `GET /donors/{id}`
- `PUT /donors/{id}`
- `POST /notifications/generate`
- `POST /notifications/send`
- `GET /notifications`
- `GET /analytics/summary`

## Sample Payloads

### Create Blood Request

```json
{
  "hospital_name": "CityCare Medical Center",
  "hospital_location": "Chicago",
  "hospital_latitude": 41.8781,
  "hospital_longitude": -87.6298,
  "contact_person": "Dr. Maria Evans",
  "blood_type_needed": "O-",
  "units_required": 2,
  "urgency_level": "High",
  "required_within_hours": 3,
  "notes": "Emergency trauma case"
}
```

### Generate Notification

```json
{
  "donor_id": "DNR-CRIT-001",
  "request_id": "<request_id>",
  "channel": "sms"
}
```

### Send Notification (Simulated)

```json
{
  "donor_id": "DNR-CRIT-001",
  "request_id": "<request_id>",
  "channel": "sms",
  "generated_message": "Urgent O- needed at CityCare in Chicago within 3 hours. Reply YES if available."
}
```

## Sample Test Flow

1. Start MongoDB locally.
2. Run backend and seed script.
3. Run frontend.
4. Open dashboard and verify summary cards.
5. Create a high/critical request.
6. Open match results and inspect ranked donors.
7. Generate AI outreach message and send simulated notification.
8. Verify notification log and analytics updates.

## Notes

- Prototype uses mock/sample donor data only.
- No real diagnosis/medical decisioning is performed.
- Notification sending is simulated for demo safety.
>>>>>>> a3f81144c587ef50313ffd6654e433970229adef
