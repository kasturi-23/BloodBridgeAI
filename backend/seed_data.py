import asyncio
import random
from datetime import datetime, timedelta
from uuid import uuid4

from app.database import db
from app.utils.blood_compatibility import ALL_BLOOD_GROUPS

FIRST_NAMES = [
    "Liam", "Noah", "Emma", "Olivia", "Ava", "Sophia", "Mason", "Lucas", "Mia", "Ethan",
    "Amelia", "James", "Harper", "Elijah", "Charlotte", "Benjamin", "Isabella", "Logan", "Evelyn", "Avery",
]
LAST_NAMES = [
    "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Rodriguez", "Martinez",
]

CITY_COORDS = [
    ("Chicago", 41.8781, -87.6298),
    ("Houston", 29.7604, -95.3698),
    ("Dallas", 32.7767, -96.7970),
    ("Austin", 30.2672, -97.7431),
    ("Phoenix", 33.4484, -112.0740),
    ("Los Angeles", 34.0522, -118.2437),
    ("New York", 40.7128, -74.0060),
    ("Seattle", 47.6062, -122.3321),
]


async def seed():
    random.seed(42)

    await db.donors.delete_many({})
    await db.requests.delete_many({})
    await db.notifications.delete_many({})

    donors = []
    for i in range(50):
        city, lat, lon = random.choice(CITY_COORDS)
        first = random.choice(FIRST_NAMES)
        last = random.choice(LAST_NAMES)

        donors.append(
            {
                "donor_id": f"DNR-{1000 + i}",
                "full_name": f"{first} {last}",
                "age": random.randint(18, 62),
                "gender": random.choice(["Male", "Female", "Other"]),
                "blood_group": random.choice(ALL_BLOOD_GROUPS),
                "city": city,
                "latitude": round(lat + random.uniform(-0.15, 0.15), 6),
                "longitude": round(lon + random.uniform(-0.15, 0.15), 6),
                "phone": f"+1-555-{random.randint(100, 999)}-{random.randint(1000, 9999)}",
                "email": f"{first.lower()}.{last.lower()}{i}@example.com",
                "last_donation_date": datetime.utcnow() - timedelta(days=random.randint(40, 320)),
                "health_screening_status": random.choices(["passed", "pending", "failed"], [0.8, 0.15, 0.05])[0],
                "eligibility_status": random.choices(["eligible", "ineligible"], [0.85, 0.15])[0],
                "availability_status": random.choices(["available", "unavailable", "busy"], [0.65, 0.2, 0.15])[0],
                "past_response_rate": round(random.uniform(0.25, 0.95), 2),
                "total_donations": random.randint(0, 24),
                "preferred_contact_method": random.choice(["sms", "email"]),
                "notes": random.choice(["", "Can travel quickly", "Prefers weekends", "Night shift worker"]),
                "contacted": False,
                "responded": random.choice([False, False, True]),
                "created_at": datetime.utcnow() - timedelta(days=random.randint(1, 180)),
            }
        )

    # Force a few strong critical-match donors in Chicago
    critical_donors = [
        {
            "donor_id": "DNR-CRIT-001",
            "full_name": "Alex Carter",
            "age": 31,
            "gender": "Male",
            "blood_group": "O-",
            "city": "Chicago",
            "latitude": 41.8905,
            "longitude": -87.6237,
            "phone": "+1-555-321-1100",
            "email": "alex.carter@example.com",
            "last_donation_date": datetime.utcnow() - timedelta(days=140),
            "health_screening_status": "passed",
            "eligibility_status": "eligible",
            "availability_status": "available",
            "past_response_rate": 0.92,
            "total_donations": 16,
            "preferred_contact_method": "sms",
            "notes": "Critical response donor",
            "contacted": False,
            "responded": True,
            "created_at": datetime.utcnow() - timedelta(days=5),
        },
        {
            "donor_id": "DNR-CRIT-002",
            "full_name": "Nina Patel",
            "age": 28,
            "gender": "Female",
            "blood_group": "O-",
            "city": "Chicago",
            "latitude": 41.8718,
            "longitude": -87.6401,
            "phone": "+1-555-321-1199",
            "email": "nina.patel@example.com",
            "last_donation_date": datetime.utcnow() - timedelta(days=132),
            "health_screening_status": "passed",
            "eligibility_status": "eligible",
            "availability_status": "available",
            "past_response_rate": 0.88,
            "total_donations": 11,
            "preferred_contact_method": "email",
            "notes": "Fast responder",
            "contacted": False,
            "responded": True,
            "created_at": datetime.utcnow() - timedelta(days=3),
        },
    ]

    donors.extend(critical_donors)
    await db.donors.insert_many(donors)

    sample_requests = [
        {
            "request_id": str(uuid4()),
            "hospital_name": "CityCare Medical Center",
            "hospital_location": "Chicago",
            "hospital_latitude": 41.8781,
            "hospital_longitude": -87.6298,
            "contact_person": "Dr. Maria Evans",
            "blood_type_needed": "O-",
            "units_required": 2,
            "urgency_level": "High",
            "required_within_hours": 3,
            "notes": "Emergency trauma case",
            "status": "pending",
            "created_at": datetime.utcnow() - timedelta(hours=2),
        },
        {
            "request_id": str(uuid4()),
            "hospital_name": "Memorial Blood Bank",
            "hospital_location": "Houston",
            "hospital_latitude": 29.7604,
            "hospital_longitude": -95.3698,
            "contact_person": "James Lin",
            "blood_type_needed": "A+",
            "units_required": 3,
            "urgency_level": "Medium",
            "required_within_hours": 12,
            "notes": "Scheduled surgery support",
            "status": "fulfilled",
            "created_at": datetime.utcnow() - timedelta(days=1),
        },
    ]

    await db.requests.insert_many(sample_requests)

    print("Seed complete: donors, requests, notifications reset and repopulated.")


if __name__ == "__main__":
    asyncio.run(seed())
