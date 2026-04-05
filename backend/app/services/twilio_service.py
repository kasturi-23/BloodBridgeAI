"""
Voice Call Service
Uses Bland.ai (free trial) for AI outbound calls.
Falls back to dev simulation mode if no API key is set.

Sign up at: https://app.bland.ai  — free trial includes call minutes.
"""
import logging
import httpx
from typing import Optional

from app.config import settings

logger = logging.getLogger(__name__)

BLAND_AI_BASE = "https://api.bland.ai/v1"


class TwilioService:
    """
    Renamed to BlandAIService internally but kept as TwilioService
    for compatibility with existing agent code.
    """

    @staticmethod
    def _normalize_phone(number: str) -> str:
        """Convert any phone format to E.164 (+1XXXXXXXXXX for US/IN etc.)."""
        import re
        digits = re.sub(r"\D", "", number)
        if number.startswith("+"):
            return "+" + digits
        # Default: assume India (+91) if 10 digits, US (+1) if 10 digits starting with common area codes
        if len(digits) == 10:
            return "+1" + digits
        if len(digits) == 11 and digits.startswith("1"):
            return "+" + digits
        return "+" + digits

    def place_call(
        self,
        to_number: str,
        request_id: str,
        call_response_id: str,
        hospital_name: str,
        blood_group: str,
    ) -> str:
        """Place an AI outbound call via Bland.ai. Returns a call ID."""
        to_number = self._normalize_phone(to_number)

        if not settings.BLAND_AI_API_KEY:
            logger.info(
                f"[DEV MODE] Simulated call to {to_number} — "
                f"request {request_id}, blood group {blood_group}"
            )
            return f"DEV_CALL_{call_response_id[:8]}"

        task = (
            f"You are the BloodBridge emergency donation assistant calling on behalf of "
            f"{hospital_name}, located at {settings.HOSPITAL_ADDRESS}. "
            f"A patient urgently requires {blood_group} blood. "
            f"Ask the donor: (1) Are you available to come to the hospital immediately? "
            f"(2) If yes — approximately how many minutes will it take you to reach the hospital? "
            f"(3) Are you feeling healthy and fit to donate today? "
            f"(4) Have you taken any medication recently that may affect donation eligibility? "
            f"If they agree to come, clearly repeat the hospital address: {settings.HOSPITAL_ADDRESS}. "
            f"Be warm, clear and brief. This is a real emergency."
        )

        webhook_url = (
            f"{settings.APP_BASE_URL}/api/call/webhook"
            f"?request_id={request_id}&call_response_id={call_response_id}"
        )

        payload = {
            "phone_number": to_number,
            "task": task,
            "model": "base",
            "language": "en",
            "voice": "maya",
            "max_duration": 5,  # minutes
            "metadata": {
                "request_id": request_id,
                "call_response_id": call_response_id,
            },
        }

        # Only attach webhook if APP_BASE_URL is a public URL (not localhost)
        if not settings.APP_BASE_URL.startswith("http://localhost"):
            payload["webhook"] = webhook_url

        try:
            resp = httpx.post(
                f"{BLAND_AI_BASE}/calls",
                json=payload,
                headers={
                    "authorization": settings.BLAND_AI_API_KEY,
                    "Content-Type": "application/json",
                },
                timeout=15,
            )
            resp.raise_for_status()
            call_id = resp.json().get("call_id", "unknown")
            logger.info(f"Bland.ai call placed to {to_number}, call_id: {call_id}")
            return call_id
        except httpx.HTTPStatusError as e:
            logger.error(f"Bland.ai call failed: {e} — response: {e.response.text}")
            raise
        except Exception as e:
            logger.error(f"Bland.ai call failed: {e}")
            raise

    def get_call_result(self, call_id: str) -> Optional[dict]:
        """
        Poll Bland.ai for the result of a completed call.
        Returns dict with keys: status, answered_by, transcript, summary
        Returns None if call is still in progress or on error.
        """
        if not settings.BLAND_AI_API_KEY or call_id.startswith("DEV_CALL_"):
            return None
        try:
            resp = httpx.get(
                f"{BLAND_AI_BASE}/calls/{call_id}",
                headers={"authorization": settings.BLAND_AI_API_KEY},
                timeout=10,
            )
            resp.raise_for_status()
            data = resp.json()
            status = data.get("status", "")
            # Only return result when call is fully done
            if status in ("completed", "no-answer", "busy", "failed"):
                return {
                    "status": status,
                    "answered_by": data.get("answered_by", ""),
                    "transcript": data.get("transcript", "") or "",
                    "summary": data.get("summary", "") or "",
                }
            return None  # still in progress
        except Exception as e:
            logger.error(f"Bland.ai poll failed for {call_id}: {e}")
            return None

    # TwiML helpers kept as stubs for compatibility — not used with Bland.ai
    def generate_twiml_greeting(self, *args, **kwargs) -> str:
        return ""

    def generate_twiml_eta(self, *args, **kwargs) -> str:
        return ""

    def generate_twiml_health_check(self, *args, **kwargs) -> str:
        return ""

    def generate_twiml_close(self, *args, **kwargs) -> str:
        return ""

    def generate_twiml_decline(self, *args, **kwargs) -> str:
        return ""
