<<<<<<< HEAD
import asyncio
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

from app.database import Base, engine
from app.routers import requests, donors, calls, dashboard, location
from app.config import settings
from app.services.call_poller import poll_active_calls

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="BloodBridge API",
    description="AI-Powered Emergency Blood Donor Coordination System",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL, "http://localhost:3000", "http://localhost:5173"],
=======
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routes.analytics import router as analytics_router
from app.routes.donors import router as donor_router
from app.routes.notifications import router as notification_router
from app.routes.requests import router as request_router

app = FastAPI(title="Blood Donor Matching System API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_origin, "http://127.0.0.1:5173"],
>>>>>>> a3f81144c587ef50313ffd6654e433970229adef
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

<<<<<<< HEAD
# Create tables on startup
@app.on_event("startup")
async def startup():
    Base.metadata.create_all(bind=engine)
    logger.info("BloodBridge API started — database tables ready")

    # Seed mock data in dev mode
    from app.seed_data import seed_if_empty
    from app.database import SessionLocal
    db = SessionLocal()
    try:
        seed_if_empty(db)
    finally:
        db.close()

    # Start background poller — checks Bland.ai every 15s for completed calls
    asyncio.create_task(poll_active_calls())
    logger.info("Call poller started — polling Bland.ai every 15s (no webhook/ngrok needed)")


# Register routers
app.include_router(requests.router)
app.include_router(donors.router)
app.include_router(calls.router)
app.include_router(dashboard.router)
app.include_router(location.router)


@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "hospital": settings.HOSPITAL_NAME,
        "version": "1.0.0",
    }


@app.get("/api/config")
def get_public_config():
    """Return non-sensitive config for the frontend."""
    return {
        "hospital_name": settings.HOSPITAL_NAME,
        "hospital_address": settings.HOSPITAL_ADDRESS,
        "hospital_lat": settings.HOSPITAL_LAT,
        "hospital_lng": settings.HOSPITAL_LNG,
    }
=======
app.include_router(donor_router)
app.include_router(request_router)
app.include_router(notification_router)
app.include_router(analytics_router)


@app.get("/")
async def health_check():
    return {"message": "Blood Donor Matching System API is running"}
>>>>>>> a3f81144c587ef50313ffd6654e433970229adef
