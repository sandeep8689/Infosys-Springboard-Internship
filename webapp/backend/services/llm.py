import httpx

from backend.config import settings


def _active_provider() -> str | None:
    p = (settings.llm_provider or "none").lower()
    if p == "openai" and settings.openai_api_key:
        return "openai"
    if p == "groq" and settings.groq_api_key:
        return "groq"
    if p == "auto":
        if settings.groq_api_key:
            return "groq"
        if settings.openai_api_key:
            return "openai"
    return None


async def _call_chat(messages: list[dict], provider: str) -> str:
    if provider == "groq":
        url = "https://api.groq.com/openai/v1/chat/completions"
        api_key = settings.groq_api_key
        model = settings.groq_model
    else:
        url = "https://api.openai.com/v1/chat/completions"
        api_key = settings.openai_api_key
        model = settings.openai_model

    async with httpx.AsyncClient(timeout=45.0) as client:
        resp = await client.post(
            url,
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
            json={"model": model, "messages": messages, "temperature": 0.3},
        )
        resp.raise_for_status()
        data = resp.json()
    return data["choices"][0]["message"]["content"].strip()


async def enhance_recommendations_async(disease: str, risk_level: str, base: dict) -> dict:
    provider = _active_provider()
    if not provider:
        return base
    prompt = (
        f"Disease: {disease}. Risk level: {risk_level}. "
        "Write exactly 3 bullet points as one paragraph: (1) one preventive care tip, "
        "(2) one lifestyle tip, (3) one follow-up tip. Plain language. "
        "Do not prescribe drug names. Educational only."
    )
    try:
        summary = await _call_chat(
            [
                {"role": "system", "content": "You are a medical education assistant."},
                {"role": "user", "content": prompt},
            ],
            provider,
        )
        base["llm_summary"] = summary
    except Exception:
        pass
    return base
