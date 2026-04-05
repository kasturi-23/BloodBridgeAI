"""
Transcript Analysis Service
Uses OpenAI to analyze a Bland.ai call transcript and determine donor decision.
"""
import json
import logging
from typing import Optional
from app.config import settings

logger = logging.getLogger(__name__)


class TranscriptAnalysisService:

    def analyze(self, transcript: str, summary: str = "") -> dict:
        """
        Send the call transcript to GPT and get a structured decision.
        Returns:
          {
            "accepted": True/False/None,
            "eta_minutes": int or None,
            "fit_to_donate": True/False/None,
            "decline_reason": str or None,
          }
        """
        if not settings.OPENAI_API_KEY:
            logger.warning("[TranscriptAnalysis] No OPENAI_API_KEY — cannot analyze transcript")
            return {"accepted": None, "eta_minutes": None, "fit_to_donate": None, "decline_reason": None}

        text = f"TRANSCRIPT:\n{transcript}\n\nSUMMARY:\n{summary}" if summary else f"TRANSCRIPT:\n{transcript}"

        prompt = (
            "You are analyzing a phone call between a blood donation coordinator AI and a potential blood donor.\n"
            "Based on the transcript below, extract the following information as JSON:\n\n"
            "- accepted (boolean): Did the donor clearly agree to come donate blood? true if yes, false if no or unclear.\n"
            "- eta_minutes (integer or null): How many minutes did the donor say it will take them to reach the hospital? null if not mentioned.\n"
            "- fit_to_donate (boolean or null): Did the donor confirm they are healthy and fit to donate today? null if not discussed.\n"
            "- decline_reason (string or null): If they declined, what reason did they give? null if they accepted.\n\n"
            "Return ONLY a valid JSON object. No explanation.\n\n"
            f"{text}"
        )

        try:
            import httpx
            response = httpx.post(
                "https://api.openai.com/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {settings.OPENAI_API_KEY}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": "gpt-4o-mini",
                    "messages": [{"role": "user", "content": prompt}],
                    "response_format": {"type": "json_object"},
                    "temperature": 0,
                },
                timeout=15,
            )
            response.raise_for_status()
            content = response.json()["choices"][0]["message"]["content"]
            result = json.loads(content)
            logger.info(f"[TranscriptAnalysis] GPT decision: {result}")
            return result
        except Exception as e:
            logger.error(f"[TranscriptAnalysis] Failed to analyze transcript: {e}")
            return {"accepted": None, "eta_minutes": None, "fit_to_donate": None, "decline_reason": None}
