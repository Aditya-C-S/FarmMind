"""
Disease Analysis Routes — wraps Aditya's run_pipeline().

POST /crops/{crop_id}/analyse-disease
  - Accepts multipart/form-data: image file + farm context fields
  - Saves image to a temp file, calls run_pipeline(), deletes temp file
  - Returns the full pipeline result as JSON

Design decisions:
  - Pipeline is imported inside the route function (lazy import), NOT at module
    level. YOLO + RF + XGBoost load ~180MB of weights synchronously at import
    time. A top-level import would block FastAPI startup and crash the entire
    backend if any model file is missing or version-mismatched.
  - If the pipeline isn't available (ImportError / FileNotFoundError), the
    route returns 503 with a clear message rather than a 500. This means the
    rest of the backend stays healthy even if Aditya's models aren't present.
  - run_pipeline() returns {"error": "..."} as a dict on failure — this is
    caught and re-raised as a 422 so the frontend gets a structured error.
  - Temp image file is always cleaned up in a finally block.
"""

import os
import tempfile
import logging

from fastapi import APIRouter, File, Form, UploadFile, HTTPException, status
from uuid import UUID

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/crops",
    tags=["Disease Analysis"],
    responses={404: {"description": "Not found"}},
)

# Market prices sourced from Aditya's app.py — Agmarknet July 2026
MARKET_PRICES = {
    "Rice":   {"Karnataka": 40.5, "Andhra Pradesh": 38.0, "Tamil Nadu": 39.0,
               "West Bengal": 37.2, "Punjab": 36.0, "Telangana": 38.5, "Other": 40.3},
    "Tomato": {"Karnataka": 22.0, "Andhra Pradesh": 35.2, "Tamil Nadu": 24.0,
               "West Bengal": 27.8, "Punjab": 20.0, "Telangana": 25.0, "Other": 24.8},
}


@router.post(
    "/{crop_id}/analyse-disease",
    summary="Run disease analysis on a leaf image",
    description=(
        "Accepts a leaf image and farm context. Runs YOLO detection → severity "
        "estimation → occurrence prediction → progression → economic loss. "
        "Returns the full diagnostic result as JSON."
    ),
)
async def analyse_disease(
    crop_id: UUID,
    image: UploadFile = File(..., description="Leaf image — JPEG or PNG"),
    crop_stage: str = Form(..., description="e.g. flowering, vegetative, tillering"),
    season: str = Form(..., description="kharif | rabi | summer | winter"),
    temperature: float = Form(28.0),
    humidity: float = Form(75.0),
    rainfall: float = Form(5.0),
    wind_speed: float = Form(10.0),
    farm_area: float = Form(2.0, description="Farm area in acres"),
    expected_yield: float = Form(5000.0, description="Expected yield in kg"),
    delay_days: int = Form(7, description="Delay scenario — days without action"),
    state: str = Form("Karnataka", description="State for market price lookup"),
):
    # ── Lazy import — keeps startup fast and backend alive if models are absent
    try:
        from pipeline import run_pipeline
    except ImportError as e:
        logger.error(f"Pipeline import failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=(
                "Disease analysis pipeline is not available. "
                "Ensure pipeline.py and the results/ model folder are present "
                "in the backend directory. Details: " + str(e)
            ),
        )
    except Exception as e:
        logger.error(f"Pipeline load error: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Pipeline failed to load: {str(e)}",
        )

    # ── Save uploaded image to a temp file
    suffix = os.path.splitext(image.filename or "leaf.jpg")[1] or ".jpg"
    tmp_path = None
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            contents = await image.read()
            tmp.write(contents)
            tmp_path = tmp.name

        # ── First pass: detect crop type to get the right market price
        first_pass = run_pipeline(
            image_path=tmp_path,
            crop_stage=crop_stage.lower(),
            season=season.lower(),
            temperature=temperature,
            humidity=humidity,
            rainfall=rainfall,
            wind_speed=wind_speed,
            farm_area=farm_area,
            expected_yield=expected_yield,
            delay_days=delay_days,
            market_price=30.0,  # placeholder for first pass
        )

        if "error" in first_pass:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=first_pass["error"],
            )

        # ── Resolve market price from detected crop + state
        detected_crop = first_pass.get("crop", "")
        market_price = MARKET_PRICES.get(detected_crop, {}).get(state, 30.0)

        # ── Second pass with real market price (mirrors Aditya's app.py logic)
        result = run_pipeline(
            image_path=tmp_path,
            crop_stage=crop_stage.lower(),
            season=season.lower(),
            temperature=temperature,
            humidity=humidity,
            rainfall=rainfall,
            wind_speed=wind_speed,
            farm_area=farm_area,
            expected_yield=expected_yield,
            delay_days=delay_days,
            market_price=market_price,
        )

        if "error" in result:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=result["error"],
            )

        # Attach the resolved market price to the response so the UI can show it
        result["market_price"] = market_price
        result["state"] = state
        return result

    finally:
        # Always clean up the temp file
        if tmp_path and os.path.exists(tmp_path):
            try:
                os.unlink(tmp_path)
            except Exception:
                pass