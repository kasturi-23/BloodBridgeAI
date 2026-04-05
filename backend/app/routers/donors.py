from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from app.database import get_db
from app.models.donor import Donor
from app.schemas.donor import DonorCreate, DonorUpdate, DonorOut

router = APIRouter(prefix="/api/donors", tags=["donors"])


@router.post("/", response_model=DonorOut, status_code=201)
def create_donor(payload: DonorCreate, db: Session = Depends(get_db)):
    existing = db.query(Donor).filter(Donor.phone_number == payload.phone_number).first()
    if existing:
        raise HTTPException(status_code=409, detail="Donor with this phone number already exists")

    donor = Donor(**payload.model_dump())
    db.add(donor)
    db.commit()
    db.refresh(donor)
    return donor


@router.get("/", response_model=List[DonorOut])
def list_donors(
    skip: int = 0,
    limit: int = 100,
    blood_group: str = None,
    active_only: bool = True,
    db: Session = Depends(get_db),
):
    q = db.query(Donor)
    if active_only:
        q = q.filter(Donor.is_active == True)
    if blood_group:
        q = q.filter(Donor.blood_group == blood_group.upper())
    return q.order_by(Donor.full_name).offset(skip).limit(limit).all()


@router.get("/{donor_id}", response_model=DonorOut)
def get_donor(donor_id: UUID, db: Session = Depends(get_db)):
    donor = db.query(Donor).filter(Donor.donor_id == donor_id).first()
    if not donor:
        raise HTTPException(status_code=404, detail="Donor not found")
    return donor


@router.patch("/{donor_id}", response_model=DonorOut)
def update_donor(donor_id: UUID, payload: DonorUpdate, db: Session = Depends(get_db)):
    donor = db.query(Donor).filter(Donor.donor_id == donor_id).first()
    if not donor:
        raise HTTPException(status_code=404, detail="Donor not found")

    for field, value in payload.model_dump(exclude_none=True).items():
        setattr(donor, field, value)

    db.commit()
    db.refresh(donor)
    return donor


@router.delete("/{donor_id}", status_code=204)
def deactivate_donor(donor_id: UUID, db: Session = Depends(get_db)):
    donor = db.query(Donor).filter(Donor.donor_id == donor_id).first()
    if not donor:
        raise HTTPException(status_code=404, detail="Donor not found")
    donor.is_active = False
    db.commit()
