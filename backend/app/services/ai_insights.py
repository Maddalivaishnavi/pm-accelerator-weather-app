"""
Optional AI-generated weather summary. Entirely opt-in:
- If no API key is configured, this returns None immediately and the
  rest of the app behaves exactly as if this feature didn't exist.
- If a key IS configured but the call fails for any reason (network,
  rate limit, bad key), it also returns None rather than raising — an
  AI summary is a nice-to-have, never a point of failure.

Priority if multiple keys are set: Gemini, then Anthropic, then OpenAI.
All three are called via plain HTTPS (no SDKs) so there's nothing extra
to install and nothing that can block the server.
"""
import os
from typing import List, Optional

import httpx

from app.schemas import CurrentWeather, DailyForecast, AirQuality

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

GEMINI_MODEL = os.environ.get("AI_INSIGHT_GEMINI_MODEL", "gemini-2.5-flash")
ANTHROPIC_MODEL = os.environ.get("AI_INSIGHT_ANTHROPIC_MODEL", "claude-haiku-4-5-20251001")
OPENAI_MODEL = os.environ.get("AI_INSIGHT_OPENAI_MODEL", "gpt-4o-mini")

TIMEOUT_SECONDS = 8.0


def _build_prompt(location: str, current: CurrentWeather, forecast: List[DailyForecast]) -> str:
    forecast_lines = "\n".join(
        f"- {d.date}: high {d.temp_max_c}°C / low {d.temp_min_c}°C, {d.description}"
        for d in forecast[:5]
    )
    return (
        f"Location: {location}\n"
        f"Current: {current.temperature_c}°C, feels like {current.feels_like_c}°C, "
        f"{current.description}, humidity {current.humidity_pct}%, wind {current.wind_speed_kmh} km/h\n"
        f"Forecast:\n{forecast_lines}\n\n"
        "Write a friendly, specific 2-3 sentence weather summary and practical "
        "takeaway for someone planning their day. No headers, no markdown, plain text."
    )


async def generate_insight(
    location: str,
    current: CurrentWeather,
    forecast: List[DailyForecast],
    air_quality: Optional[AirQuality] = None,
) -> Optional[str]:
    if not forecast:
        return None

    prompt = _build_prompt(location, current, forecast)

    if GEMINI_API_KEY:
        return await _try(_call_gemini, prompt)
    if ANTHROPIC_API_KEY:
        return await _try(_call_anthropic, prompt)
    if OPENAI_API_KEY:
        return await _try(_call_openai, prompt)
    return None  # no key configured — feature silently disabled


async def _try(fn, prompt: str) -> Optional[str]:
    try:
        return await fn(prompt)
    except Exception:
        return None  # never let this break the main weather response


async def _call_gemini(prompt: str) -> str:
    async with httpx.AsyncClient(timeout=TIMEOUT_SECONDS) as client:
        resp = await client.post(
            f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent",
            headers={
                "x-goog-api-key": GEMINI_API_KEY,
                "content-type": "application/json",
            },
            json={"contents": [{"parts": [{"text": prompt}]}]},
        )
        resp.raise_for_status()
        data = resp.json()
        candidates = data.get("candidates", [])
        if not candidates:
            return ""
        parts = candidates[0].get("content", {}).get("parts", [])
        return "".join(p.get("text", "") for p in parts).strip()


async def _call_anthropic(prompt: str) -> str:
    async with httpx.AsyncClient(timeout=TIMEOUT_SECONDS) as client:
        resp = await client.post(
            "https://api.anthropic.com/v1/messages",
            headers={
                "x-api-key": ANTHROPIC_API_KEY,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json",
            },
            json={
                "model": ANTHROPIC_MODEL,
                "max_tokens": 200,
                "messages": [{"role": "user", "content": prompt}],
            },
        )
        resp.raise_for_status()
        data = resp.json()
        return "".join(
            block.get("text", "") for block in data.get("content", []) if block.get("type") == "text"
        ).strip()


async def _call_openai(prompt: str) -> str:
    async with httpx.AsyncClient(timeout=TIMEOUT_SECONDS) as client:
        resp = await client.post(
            "https://api.openai.com/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENAI_API_KEY}",
                "content-type": "application/json",
            },
            json={
                "model": OPENAI_MODEL,
                "max_tokens": 200,
                "messages": [{"role": "user", "content": prompt}],
            },
        )
        resp.raise_for_status()
        data = resp.json()
        return data["choices"][0]["message"]["content"].strip()