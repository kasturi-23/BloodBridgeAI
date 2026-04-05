from openai import AsyncOpenAI

from app.config import settings

client = AsyncOpenAI(api_key=settings.openai_api_key) if settings.openai_api_key else None


async def generate_outreach_message(channel: str, donor: dict, request_doc: dict):
    fallback = (
        f"Urgent blood request: {request_doc['blood_type_needed']} needed at {request_doc['hospital_name']} "
        f"({request_doc['hospital_location']}) within {request_doc['required_within_hours']} hours. "
        "Please reply YES if you can help."
    )
    if not client:
        return fallback

    prompt = (
        f"Generate a {channel.upper()} outreach message under 250 characters."
        "Be polite, clear, and urgent. "
        f"Hospital: {request_doc['hospital_name']}. "
        f"Blood type needed: {request_doc['blood_type_needed']}. "
        f"City: {request_doc['hospital_location']}. "
        f"Required within: {request_doc['required_within_hours']} hours. "
        f"Donor first name: {donor['full_name'].split()[0]}."
    )

    try:
        completion = await client.chat.completions.create(
            model=settings.openai_model,
            messages=[
                {"role": "system", "content": "You write concise healthcare outreach messages."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.4,
            max_tokens=120,
        )
        text = completion.choices[0].message.content
        return (text or fallback).strip()
    except Exception:
        return fallback


async def generate_match_summary(request_doc: dict, matches: list[dict]):
    if not matches:
        return "No eligible donors were found. Expand radius, relax timing, or create a wider outreach campaign."

    top = matches[:3]
    nearby = sum(1 for m in matches if m["distance_miles"] <= 5)
    high_resp = sum(1 for m in matches if m["response_probability"] >= 0.7)

    fallback = (
        f"{len(matches)} eligible donors were found for {request_doc['blood_type_needed']}. "
        f"{nearby} are within 5 miles and {high_resp} have high historical responsiveness. "
        f"Contact top donors now, including {', '.join(m['full_name'] for m in top)}."
    )

    if not client:
        return fallback

    prompt = (
        "Generate a short natural language summary (2-3 sentences) for blood donor match results. "
        f"Request: blood type {request_doc['blood_type_needed']}, urgency {request_doc['urgency_level']}, "
        f"required within {request_doc['required_within_hours']} hours. "
        f"Total matches: {len(matches)}. Nearby donors (<=5 miles): {nearby}. High responsiveness donors: {high_resp}. "
        f"Top donor names: {', '.join(m['full_name'] for m in top)}."
    )

    try:
        completion = await client.chat.completions.create(
            model=settings.openai_model,
            messages=[
                {"role": "system", "content": "You summarize donor matching results for hospital staff."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.4,
            max_tokens=160,
        )
        text = completion.choices[0].message.content
        return (text or fallback).strip()
    except Exception:
        return fallback
