"""
Seed mock donor data for development / demo purposes.
"""
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.models.donor import Donor
import logging

logger = logging.getLogger(__name__)

MOCK_DONORS = [
    {
        "full_name": "James Okafor",
        "phone_number": "+13124042616",
        "blood_group": "O+",
        "age": 32,
        "weight": 78.0,
        "address": "45 Maple Street, City",
        "latitude": 40.7200,
        "longitude": -74.0020,
        "last_donation_date": datetime.utcnow() - timedelta(days=90),
        "screening_status": "cleared",
        "medication_flag": False,
        "temporary_deferral_flag": False,
        "availability_status": "available",
        "past_response_score": 0.9,
    },
    {
        "full_name": "Aisha Mohammed",
        "phone_number": "+18726640766",
        "blood_group": "A+",
        "age": 27,
        "weight": 62.0,
        "address": "112 Oak Avenue, City",
        "latitude": 40.7050,
        "longitude": -74.0100,
        "last_donation_date": datetime.utcnow() - timedelta(days=120),
        "screening_status": "cleared",
        "medication_flag": False,
        "temporary_deferral_flag": False,
        "availability_status": "available",
        "past_response_score": 0.85,
    },
    {
        "full_name": "Carlos Rivera",
        "phone_number": "+13125550125",
        "blood_group": "O-",
        "age": 45,
        "weight": 85.0,
        "address": "88 Pine Road, City",
        "latitude": 40.7300,
        "longitude": -73.9980,
        "last_donation_date": datetime.utcnow() - timedelta(days=200),
        "screening_status": "cleared",
        "medication_flag": False,
        "temporary_deferral_flag": False,
        "availability_status": "available",
        "past_response_score": 0.95,
    },
    {
        "full_name": "Priya Sharma",
        "phone_number": "+13125550126",
        "blood_group": "B+",
        "age": 29,
        "weight": 58.0,
        "address": "23 Elm Street, City",
        "latitude": 40.7150,
        "longitude": -74.0200,
        "last_donation_date": datetime.utcnow() - timedelta(days=30),  # Too recent!
        "screening_status": "cleared",
        "medication_flag": False,
        "temporary_deferral_flag": False,
        "availability_status": "available",
        "past_response_score": 0.75,
    },
    {
        "full_name": "Michael Chen",
        "phone_number": "+13125550127",
        "blood_group": "AB+",
        "age": 38,
        "weight": 72.0,
        "address": "67 Cedar Lane, City",
        "latitude": 40.7080,
        "longitude": -73.9950,
        "last_donation_date": datetime.utcnow() - timedelta(days=180),
        "screening_status": "cleared",
        "medication_flag": True,  # Has medication flag
        "temporary_deferral_flag": False,
        "availability_status": "available",
        "past_response_score": 0.6,
    },
    {
        "full_name": "Fatima Al-Hassan",
        "phone_number": "+13125550128",
        "blood_group": "O+",
        "age": 31,
        "weight": 65.0,
        "address": "190 Birch Blvd, City",
        "latitude": 40.7250,
        "longitude": -74.0050,
        "last_donation_date": datetime.utcnow() - timedelta(days=100),
        "screening_status": "cleared",
        "medication_flag": False,
        "temporary_deferral_flag": False,
        "availability_status": "available",
        "past_response_score": 0.8,
    },
    {
        "full_name": "David Kim",
        "phone_number": "+13125550129",
        "blood_group": "A-",
        "age": 52,
        "weight": 80.0,
        "address": "34 Willow Way, City",
        "latitude": 40.7400,
        "longitude": -73.9900,
        "last_donation_date": datetime.utcnow() - timedelta(days=365),
        "screening_status": "cleared",
        "medication_flag": False,
        "temporary_deferral_flag": False,
        "availability_status": "available",
        "past_response_score": 0.7,
    },
    {
        "full_name": "Sofia Petrov",
        "phone_number": "+13125550130",
        "blood_group": "B-",
        "age": 24,
        "weight": 55.0,
        "address": "55 Spruce Street, City",
        "latitude": 40.7100,
        "longitude": -74.0150,
        "last_donation_date": datetime.utcnow() - timedelta(days=70),
        "screening_status": "cleared",
        "medication_flag": False,
        "temporary_deferral_flag": True,  # Temporarily deferred
        "temporary_deferral_until": datetime.utcnow() + timedelta(days=14),
        "availability_status": "available",
        "past_response_score": 0.65,
    },
    {
        "full_name": "Ahmed Yusuf",
        "phone_number": "+13125550131",
        "blood_group": "O+",
        "age": 36,
        "weight": 90.0,
        "address": "201 Ash Avenue, City",
        "latitude": 40.7180,
        "longitude": -74.0080,
        "last_donation_date": None,  # First-time donor
        "screening_status": "cleared",
        "medication_flag": False,
        "temporary_deferral_flag": False,
        "availability_status": "available",
        "past_response_score": 0.5,
    },
    {
        "full_name": "Linda Nwosu",
        "phone_number": "+13125550132",
        "blood_group": "AB-",
        "age": 41,
        "weight": 68.0,
        "address": "76 Poplar Place, City",
        "latitude": 40.7320,
        "longitude": -73.9970,
        "last_donation_date": datetime.utcnow() - timedelta(days=150),
        "screening_status": "cleared",
        "medication_flag": False,
        "temporary_deferral_flag": False,
        "availability_status": "available",
        "past_response_score": 0.88,
    },
]


def seed_if_empty(db: Session):
    """Seed mock donors only if no donors exist yet."""
    donor_count = db.query(Donor).count()
    if donor_count > 0:
        logger.info(f"Found {donor_count} existing donors. Skipping seed.")
        return

    logger.info("No donors found. Seeding mock data...")
    from app.models.call_response import CallResponse
    from app.models.hospital_request import HospitalRequest

    # Clear any existing data
    db.query(CallResponse).delete()
    db.query(HospitalRequest).delete()
    db.query(Donor).delete()
    db.commit()

    for data in MOCK_DONORS:
        donor = Donor(**data)
        db.add(donor)

    db.commit()
    logger.info(f"Seeded {len(MOCK_DONORS)} mock donors into the database")
