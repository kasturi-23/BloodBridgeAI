from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from datetime import datetime

from app.database import get_db
from app.models.call_response import CallResponse
from app.schemas.call_response import LocationConsentPayload

router = APIRouter(prefix="/api/location", tags=["location"])


@router.post("/consent")
def store_location_consent(
    payload: LocationConsentPayload,
    db: Session = Depends(get_db),
):
    """Store donor-consented location coordinates."""
    record = (
        db.query(CallResponse)
        .filter(CallResponse.location_share_token == payload.token)
        .first()
    )
    if not record:
        raise HTTPException(status_code=404, detail="Invalid or expired location token")

    record.donor_latitude = payload.latitude
    record.donor_longitude = payload.longitude
    record.location_consent = True
    db.commit()

    return {"message": "Location received. Thank you!"}


@router.get("/share/{token}", response_class=HTMLResponse)
def location_share_page(token: str, db: Session = Depends(get_db)):
    """
    Consent-based location sharing page sent to donor via SMS.
    Donor opens this link and approves sharing their location.
    """
    record = (
        db.query(CallResponse)
        .filter(CallResponse.location_share_token == token)
        .first()
    )
    if not record:
        return HTMLResponse(content="<h2>Invalid or expired link.</h2>", status_code=404)

    return HTMLResponse(content=f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8"/>
    <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
    <title>BloodBridge — Share Location</title>
    <style>
        body {{ font-family: sans-serif; max-width: 420px; margin: 40px auto; padding: 20px;
                text-align: center; }}
        h1 {{ color: #c0392b; }}
        .btn {{ background: #c0392b; color: #fff; border: none; padding: 16px 32px;
               font-size: 18px; border-radius: 8px; cursor: pointer; margin-top: 20px; }}
        .btn:disabled {{ background: #aaa; }}
        #status {{ margin-top: 16px; font-size: 14px; color: #555; }}
    </style>
</head>
<body>
    <h1>BloodBridge</h1>
    <p>The hospital would like to track your location to estimate your arrival time.</p>
    <p><strong>This is completely optional and will only be used for this emergency.</strong></p>
    <button class="btn" id="shareBtn" onclick="shareLocation()">Share My Location</button>
    <div id="status"></div>
    <script>
        async function shareLocation() {{
            const btn = document.getElementById('shareBtn');
            const status = document.getElementById('status');
            btn.disabled = true;
            status.textContent = 'Getting your location...';

            if (!navigator.geolocation) {{
                status.textContent = 'Geolocation not supported on this device.';
                btn.disabled = false;
                return;
            }}

            navigator.geolocation.getCurrentPosition(async (pos) => {{
                const {{ latitude, longitude }} = pos.coords;
                try {{
                    const resp = await fetch('/api/location/consent', {{
                        method: 'POST',
                        headers: {{ 'Content-Type': 'application/json' }},
                        body: JSON.stringify({{ token: '{token}', latitude, longitude }}),
                    }});
                    if (resp.ok) {{
                        status.textContent = 'Location shared successfully. Thank you!';
                        btn.textContent = 'Shared';
                    }} else {{
                        status.textContent = 'Could not share location. Please try again.';
                        btn.disabled = false;
                    }}
                }} catch (e) {{
                    status.textContent = 'Network error. Please try again.';
                    btn.disabled = false;
                }}
            }}, (err) => {{
                status.textContent = 'Could not get location: ' + err.message;
                btn.disabled = false;
            }});
        }}
    </script>
</body>
</html>""")
