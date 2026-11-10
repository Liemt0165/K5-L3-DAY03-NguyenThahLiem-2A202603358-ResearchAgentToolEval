from __future__ import annotations

from typing import Any
import requests

from tools._shared import TIMEOUT, err


def get_weather(location: str = "") -> dict[str, Any]:
    """Get current weather for a city or location using wttr.in public service."""
    cleaned_loc = " ".join((location or "").split())
    if not cleaned_loc:
        return {
            "tool": "weather",
            "error": "ValueError",
            "message": "location must not be empty.",
            "location": "",
        }

    try:
        url = f"https://wttr.in/{cleaned_loc}"
        resp = requests.get(
            url,
            params={"format": "j1"},
            headers={"User-Agent": "AI20k-WeatherAgent/1.0"},
            timeout=TIMEOUT,
        )
        resp.raise_for_status()
        data = resp.json()
        current = (data.get("current_condition") or [{}])[0]
        area = (data.get("nearest_area") or [{}])[0]

        temp = current.get("temp_C")
        wind = current.get("windspeedKmph")
        desc = ((current.get("weatherDesc") or [{}])[0]).get("value", "")

        city = ((area.get("areaName") or [{}])[0]).get("value", cleaned_loc)
        country = ((area.get("country") or [{}])[0]).get("value", "")
        full_loc = f"{city}, {country}".strip(", ") or cleaned_loc

        return {
            "tool": "weather",
            "location": full_loc,
            "temperature": f"{temp}°C" if temp is not None else "unknown",
            "windspeed": f"{wind} km/h" if wind is not None else "unknown",
            "weather_condition": desc or "unknown",
            "status": "success",
        }
    except Exception as exc:
        return err("weather", exc)
