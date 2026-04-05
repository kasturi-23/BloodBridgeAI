"""
Notification Service
Sends donor directions and confirmations via Email (Gmail SMTP — free)
or falls back to console logging in dev mode.
"""
import smtplib
import logging
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from app.config import settings

logger = logging.getLogger(__name__)


class SMSService:
    """
    Despite the name (kept for compatibility), this now sends emails via Gmail SMTP.
    Set GMAIL_USER and GMAIL_APP_PASSWORD in .env to enable real sending.
    Without credentials it logs to console (dev mode).
    """

    def _get_donor_email(self, phone_or_email: str) -> str:
        """
        In production, look up the donor's email from DB.
        Here we accept either a phone number or email address directly.
        If it looks like a phone number, we fall back to dev mode.
        """
        if "@" in phone_or_email:
            return phone_or_email
        return None  # phone-only donors → dev mode log

    def send_sms(self, to: str, body: str) -> bool:
        """Send notification. `to` can be an email address or phone number."""
        email = self._get_donor_email(to)

        if not email:
            # Phone-only donor in dev mode — log to console
            logger.info(f"\n{'='*50}\n[DEV NOTIFICATION] To: {to}\n{body}\n{'='*50}")
            return True

        return self._send_email(
            to_email=email,
            subject="BloodBridge — Emergency Donation Confirmation",
            body=body,
        )

    def send_map_link(
        self,
        to: str,
        hospital_name: str,
        hospital_address: str,
        hospital_lat: float,
        hospital_lng: float,
        location_share_url: str = None,
    ) -> bool:
        maps_link = (
            f"https://www.google.com/maps/dir/?api=1"
            f"&destination={hospital_lat},{hospital_lng}"
        )
        plain_body = (
            f"BloodBridge — Thank you for agreeing to donate!\n\n"
            f"Please head to:\n{hospital_name}\n{hospital_address}\n\n"
            f"Directions: {maps_link}"
        )
        if location_share_url:
            plain_body += f"\n\nShare your location with the hospital: {location_share_url}"

        html_body = f"""
<div style="font-family:sans-serif;max-width:480px;margin:auto;padding:24px">
  <div style="background:#dc2626;color:white;padding:16px 24px;border-radius:12px 12px 0 0">
    <h2 style="margin:0">🩸 BloodBridge — Donation Confirmed</h2>
  </div>
  <div style="border:1px solid #fecaca;border-top:none;padding:24px;border-radius:0 0 12px 12px">
    <p style="font-size:16px">Thank you for agreeing to donate. Please proceed to:</p>
    <div style="background:#fef2f2;border-left:4px solid #dc2626;padding:12px 16px;margin:16px 0;border-radius:4px">
      <strong>{hospital_name}</strong><br/>
      <span style="color:#555">{hospital_address}</span>
    </div>
    <a href="{maps_link}"
       style="display:inline-block;background:#dc2626;color:white;padding:12px 24px;
              border-radius:8px;text-decoration:none;font-weight:bold;margin:8px 0">
      Get Directions
    </a>
    {"<br/><br/><a href='" + location_share_url + "' style='color:#dc2626'>Share your location with the hospital</a>" if location_share_url else ""}
    <p style="color:#888;font-size:12px;margin-top:24px">
      This message was sent by BloodBridge Emergency Coordination System.
    </p>
  </div>
</div>"""

        email = self._get_donor_email(to)
        if not email:
            logger.info(f"\n{'='*50}\n[DEV NOTIFICATION] To: {to}\n{plain_body}\n{'='*50}")
            return True

        return self._send_email(
            to_email=email,
            subject="BloodBridge — Please head to the hospital now",
            body=plain_body,
            html_body=html_body,
        )

    def _send_email(self, to_email: str, subject: str, body: str, html_body: str = None) -> bool:
        if not settings.GMAIL_USER or not settings.GMAIL_APP_PASSWORD:
            logger.info(
                f"\n{'='*50}\n[DEV EMAIL] To: {to_email}\nSubject: {subject}\n{body}\n{'='*50}"
            )
            return True

        try:
            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = f"BloodBridge <{settings.GMAIL_USER}>"
            msg["To"] = to_email

            msg.attach(MIMEText(body, "plain"))
            if html_body:
                msg.attach(MIMEText(html_body, "html"))

            with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
                server.login(settings.GMAIL_USER, settings.GMAIL_APP_PASSWORD)
                server.sendmail(settings.GMAIL_USER, to_email, msg.as_string())

            logger.info(f"Email sent to {to_email}")
            return True

        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {e}")
            return False
