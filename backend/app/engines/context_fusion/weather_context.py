"""
Weather Context
---------------
Cross-references live weather (Open-Meteo) against the current crop's
weather_guidelines (from its knowledge base JSON) to determine which
guidelines are actually triggered right now.

Design note — why this calls Open-Meteo directly instead of reading from
our own Phase 2 WeatherCache/WeatherService: the team's weather fetch
(used at "Analyse" time, feeding the severity/economic-loss model) is
purely in-the-moment and never persisted. That means WeatherCache never
actually accumulates real data, so building this against it would have
produced a component that silently never fires. Calling Open-Meteo
directly here is fully decoupled from that other flow — same principle
as the disease detection contract: no dependency on a teammate's code or
data pipeline being finished or persisted anywhere.

This module additionally requests `past_days` from Open-Meteo (the
teammate's fetch_weather() only pulls today's data), since the drought
check needs a trailing window, not a single snapshot. Open-Meteo supports
this in the same forecast endpoint at no extra cost.

Known simplification: the "high_temperature" instant check uses the
current instantaneous temperature reading (matching the teammate's
fetch_weather() field, temperature_2m), not a true daily max — a live
single-point read doesn't have "today's max" the way a stored daily
record would. Threshold below is set slightly lower than the original
daily-max threshold to compensate; revisit if this causes false negatives
in practice.
"""

from dataclasses import dataclass
from datetime import date
from functools import lru_cache
from typing import Any, Dict, List, Optional

from app.services.weather_service import WeatherService
from app.services.weather_intelligence_service import WeatherIntelligenceService

import requests

_OPEN_METEO_URL = "https://api.open-meteo.com/v1/forecast"
_REQUEST_TIMEOUT_SECONDS = 5
_DROUGHT_LOOKBACK_DAYS = 10

# --- MVP trigger thresholds (see module docstring) ---------------------
_INSTANT_RULES: Dict[str, Dict[str, Any]] = {
    "high_humidity": {
        "check": lambda w: w["humidity"] is not None and w["humidity"] >= 80,
        "observed": lambda w: f"{w['humidity']}% humidity (live reading)",
    },
    "heavy_rainfall": {
        "check": lambda w: w["rainfall_today"] is not None and w["rainfall_today"] >= 50,
        "observed": lambda w: f"{w['rainfall_today']}mm rainfall today",
    },
    "high_temperature": {
        # Slightly lower than a true daily-max threshold — see module docstring.
        "check": lambda w: w["temperature"] is not None and w["temperature"] >= 33,
        "observed": lambda w: f"{w['temperature']}°C (live reading)",
    },
}

_DROUGHT_MIN_RECORDS = 5
_DROUGHT_RAINFALL_THRESHOLD_MM = 1.0


@lru_cache(maxsize=256)
def _fetch_open_meteo_cached(latitude: float, longitude: float, cache_bucket: str) -> Optional[Dict[str, Any]]:
    """
    Actual HTTP call, cached per (lat, lon, day). `cache_bucket` is a plain
    date string so the cache naturally invalidates once per day without
    needing a real TTL mechanism — good enough for MVP call volume.
    Returns None on any request failure (network, timeout, bad response)
    rather than raising, so a flaky API call degrades the feature rather
    than breaking the whole fused response.
    """
    try:
        response = requests.get(
            _OPEN_METEO_URL,
            params={
                "latitude": latitude,
                "longitude": longitude,
                "current": "temperature_2m,relative_humidity_2m,rain,wind_speed_10m",
                "daily": "rain_sum",
                "past_days": _DROUGHT_LOOKBACK_DAYS,
                "forecast_days": 1,
                "timezone": "auto",
            },
            timeout=_REQUEST_TIMEOUT_SECONDS,
        )
        response.raise_for_status()
        return response.json()
    except (requests.RequestException, ValueError):
        return None


def _parse_current(raw: Dict[str, Any]) -> Dict[str, Optional[float]]:
    current = raw.get("current", {})
    return {
        "temperature": current.get("temperature_2m"),
        "humidity": current.get("relative_humidity_2m"),
        "rainfall_today": current.get("rain"),
        "wind_speed": current.get("wind_speed_10m"),
    }


def _parse_daily_rainfall(raw: Dict[str, Any]) -> List[float]:
    daily = raw.get("daily", {})
    rain_sum = daily.get("rain_sum", [])
    # Exclude today (last entry) from the drought trend — today is already
    # covered by the heavy_rainfall instant check above.
    return [r for r in rain_sum[:-1] if r is not None]


def _check_drought(daily_rainfall: List[float]) -> bool:
    if len(daily_rainfall) < _DROUGHT_MIN_RECORDS:
        return False
    return all(r < _DROUGHT_RAINFALL_THRESHOLD_MM for r in daily_rainfall)


def get_weather_context(
    latitude: Optional[float],
    longitude: Optional[float],
    crop_type:str,
    crop_stage: str,
    crop_data: Dict[str, Any],
    as_of: Optional[date] = None,
) -> Dict[str, Any]:
    """
    Determine which of the crop's weather_guidelines are currently triggered,
    using live Open-Meteo data for the field's coordinates.

    Args:
        latitude, longitude: the field's coordinates. If either is None
            (field has no coordinates recorded), returns data_available=False
            immediately rather than calling the API.
        crop_data: full crop knowledge base (for weather_guidelines)
        as_of: reference date, used only for the cache bucket key; defaults to today

    Returns:
        {
            "data_available": bool,
            "source": "open-meteo" | None,
            "triggered_alerts": [...],
        }
    """
    _null_current = {"temperature": None, "humidity": None, "rainfall_today": None, "wind_speed": None}

    if latitude is None or longitude is None:
        return {
            "data_available": False,
            "source": None,
            "current": _null_current,
            "triggered_alerts": [],
            "reason": "Field has no recorded coordinates.",
        }

    reference_date = as_of or date.today()
    raw = _fetch_open_meteo_cached(latitude, longitude, reference_date.isoformat())

    if raw is None:
        return {
            "data_available": False,
            "source": "open-meteo",
            "current": _null_current,
            "triggered_alerts": [],
            "reason": "Open-Meteo request failed or timed out.",
        }

    current = _parse_current(raw)
    daily_rainfall = _parse_daily_rainfall(raw)

    forecast = WeatherService.fetch_5_day_forecast(
        latitude,
        longitude
    )
    if forecast is None:
        return {
            "data_available": False,
            "forecast": [],
            "irrigation": {},
            "prevention": [],
            "triggered_alerts": [],
        }

    if crop_stage.lower() == "harvest":
        irrigation = None
    else:
        irrigation = WeatherIntelligenceService.irrigation_advice(
            crop_type,
            forecast
        )

    prevention = WeatherIntelligenceService.disease_prevention(
        crop_type,
        forecast
    )

    guidelines = crop_data.get("weather_guidelines", [])
    guidelines_by_id = {g["weather_id"]: g for g in guidelines}

    triggered: List[Dict[str, Any]] = []

    for weather_id, rule in _INSTANT_RULES.items():
        if weather_id not in guidelines_by_id:
            continue
        if rule["check"](current):
            g = guidelines_by_id[weather_id]
            triggered.append(
                {
                    "weather_id": weather_id,
                    "condition": g.get("condition"),
                    "effect": g.get("effect", []),
                    "observed": rule["observed"](current),
                }
            )

    if "drought" in guidelines_by_id and _check_drought(daily_rainfall):
        g = guidelines_by_id["drought"]
        total = sum(daily_rainfall)
        triggered.append(
            {
                "weather_id": "drought",
                "condition": g.get("condition"),
                "effect": g.get("effect", []),
                "observed": f"{total:.1f}mm total rainfall over the last {len(daily_rainfall)} days",
            }
        )

    return {
        "data_available": True,
        "source": "open-meteo",

        "current": {
            "temperature": current["temperature"],
            "humidity": current["humidity"],
            "rainfall_today": current["rainfall_today"],
            "wind_speed": current["wind_speed"],
        },
        "forecast": forecast,

        "irrigation": irrigation,

        "prevention": prevention,

        "triggered_alerts": triggered,
    }