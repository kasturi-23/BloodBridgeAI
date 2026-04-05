"""
Eligibility Agent
Responsibility: Verify whether shortlisted donors can donate right now.
Inputs: Last donation date, screening status, medication/illness flags, deferrals, availability.
Outputs: Eligible donor list with rejection reasons for ineligible ones.
"""
from typing import List, Dict, Any, Tuple
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
import logging

from app.models.donor import Donor

logger = logging.getLogger(__name__)

# Minimum days between whole-blood donations (56 days = 8 weeks)
MIN_DONATION_INTERVAL_DAYS = 56

# Minimum age and weight requirements
MIN_AGE = 17
MIN_WEIGHT_KG = 50.0


class EligibilityAgent:
    """
    Agent 2: Filter shortlisted donors for medical and operational eligibility.
    """

    def __init__(self, db: Session):
        self.db = db

    def check_donor(self, donor: Donor) -> Tuple[bool, str]:
        """
        Check a single donor's eligibility.
        Returns (is_eligible, reason_if_not).
        """
        now = datetime.utcnow()

        # 1. Active status check
        if not donor.is_active:
            return False, "Donor account is inactive"

        # 2. Availability
        if donor.availability_status != "available":
            return False, f"Donor marked as {donor.availability_status}"

        # 3. Screening status
        if donor.screening_status == "failed":
            return False, "Donor failed medical screening"
        if donor.screening_status == "pending":
            return False, "Donor screening is pending review"

        # 4. Temporary deferral
        if donor.temporary_deferral_flag:
            if donor.temporary_deferral_until and donor.temporary_deferral_until > now:
                days_left = (donor.temporary_deferral_until - now).days
                return False, f"Temporarily deferred for {days_left} more day(s)"
            elif not donor.temporary_deferral_until:
                return False, "Temporarily deferred (no end date set — requires manual review)"

        # 5. Medication flag
        if donor.medication_flag:
            return False, "Donor has active medication flag — requires manual review"

        # 6. Last donation interval
        if donor.last_donation_date:
            days_since = (now - donor.last_donation_date).days
            if days_since < MIN_DONATION_INTERVAL_DAYS:
                days_to_wait = MIN_DONATION_INTERVAL_DAYS - days_since
                return False, f"Must wait {days_to_wait} more day(s) after last donation"

        # 7. Age check
        if donor.age is not None and donor.age < MIN_AGE:
            return False, f"Donor is under minimum age ({MIN_AGE})"

        # 8. Weight check
        if donor.weight is not None and donor.weight < MIN_WEIGHT_KG:
            return False, f"Donor is under minimum weight ({MIN_WEIGHT_KG}kg)"

        return True, ""

    def run(
        self,
        shortlisted: List[Dict[str, Any]],
    ) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        """
        Filter shortlisted donors into eligible and ineligible.
        Returns (eligible_list, ineligible_list) where each item includes rejection_reason.
        """
        eligible = []
        ineligible = []

        for item in shortlisted:
            donor: Donor = item["donor"]
            is_eligible, reason = self.check_donor(donor)

            if is_eligible:
                eligible.append(item)
                logger.debug(f"[EligibilityAgent] Donor {donor.donor_id} ({donor.full_name}): ELIGIBLE")
            else:
                item["rejection_reason"] = reason
                ineligible.append(item)
                logger.info(
                    f"[EligibilityAgent] Donor {donor.donor_id} ({donor.full_name}): "
                    f"INELIGIBLE — {reason}"
                )

        logger.info(
            f"[EligibilityAgent] {len(eligible)} eligible, "
            f"{len(ineligible)} ineligible from {len(shortlisted)} shortlisted"
        )
        return eligible, ineligible
