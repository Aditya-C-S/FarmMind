"""
Tests for Pydantic schemas (models, schemas, all three folders).
These are pure validation tests — no DB required.
"""

import pytest
import uuid
from datetime import date
from pydantic import ValidationError

# ── Phase 1 schemas ──────────────────────────────────────────────────────────
from app.schemas.farmer import FarmerCreate, FarmerUpdate, FarmerResponse
from app.schemas.field  import FieldCreate,  FieldUpdate,  FieldResponse
from app.schemas.crop   import CropCreate,   CropUpdate,   CropResponse, CropStatus

# ── Phase 2 schemas ──────────────────────────────────────────────────────────
from app.schemas.activity_log           import ActivityLogCreate, ActivityLogUpdate, ActivityLogResponse
from app.schemas.disease_history        import DiseaseHistoryCreate, DiseaseHistoryUpdate, DiseaseHistoryResponse
from app.schemas.irrigation             import IrrigationCreate, IrrigationUpdate, IrrigationResponse
from app.schemas.fertilizer_application import FertilizerApplicationCreate, FertilizerApplicationUpdate, FertilizerApplicationResponse
from app.schemas.weather_cache          import WeatherCacheCreate, WeatherCacheUpdate, WeatherCacheResponse


# ===========================================================================
# FarmerCreate
# ===========================================================================
class TestFarmerSchema:
    def test_valid(self):
        f = FarmerCreate(name="Ramu", phone="9876543210", district="Tanjore", state="TN", email="ramu@farmmind.com")
        assert f.name == "Ramu"
        assert f.district == "Tanjore"

    def test_empty_name_rejected(self):
        with pytest.raises(ValidationError):
            FarmerCreate(name="", phone="9876543210", district="X", state="Y")

    def test_optional_email(self):
        f = FarmerCreate(name="Ramu", phone="9876543210", district="X", state="Y", email="ramu@test.com")
        assert f.email == "ramu@test.com"

    def test_update_partial(self):
        u = FarmerUpdate(district="Chennai")
        assert u.district == "Chennai"
        assert u.name is None  # unset fields are None


# ===========================================================================
# FieldCreate
# ===========================================================================
class TestFieldSchema:
    def test_valid(self):
        f = FieldCreate(farmer_id=uuid.uuid4(), field_name="East Plot", area_acres=7.25)
        assert f.field_name == "East Plot"

    def test_with_coordinates(self):
        f = FieldCreate(
            farmer_id=uuid.uuid4(),
            field_name="North Plot",
            area_acres=3.0,
            latitude=11.123456,
            longitude=79.654321,
        )
        assert float(f.latitude) == 11.123456

    def test_update_partial(self):
        u = FieldUpdate(soil_type="Black Cotton")
        assert u.soil_type == "Black Cotton"
        assert u.field_name is None


# ===========================================================================
# CropCreate
# ===========================================================================
class TestCropSchema:
    def test_valid(self):
        c = CropCreate(
            field_id=uuid.uuid4(),
            crop_type="Tomato",
            sowing_date=date(2025, 1, 1),
            expected_harvest_date=date(2025, 4, 1),
        )
        assert c.crop_type == "Tomato"
        assert c.status == CropStatus.ACTIVE  # default

    def test_invalid_dates(self):
        """Harvest date before sowing date must fail."""
        with pytest.raises(ValidationError):
            CropCreate(
                field_id=uuid.uuid4(),
                crop_type="Wheat",
                sowing_date=date(2025, 6, 1),
                expected_harvest_date=date(2025, 1, 1),
            )

    def test_same_dates_rejected(self):
        with pytest.raises(ValidationError):
            CropCreate(
                field_id=uuid.uuid4(),
                crop_type="Wheat",
                sowing_date=date(2025, 6, 1),
                expected_harvest_date=date(2025, 6, 1),
            )

    def test_status_enum(self):
        c = CropCreate(
            field_id=uuid.uuid4(),
            crop_type="Rice",
            sowing_date=date(2025, 1, 1),
            expected_harvest_date=date(2025, 6, 1),
            status=CropStatus.HARVESTED,
        )
        assert c.status == CropStatus.HARVESTED

    def test_update_partial(self):
        u = CropUpdate(status=CropStatus.FAILED)
        assert u.status == CropStatus.FAILED
        assert u.crop_type is None


# ===========================================================================
# ActivityLogCreate
# ===========================================================================
class TestActivityLogSchema:
    def test_valid_with_metadata(self):
        a = ActivityLogCreate(
            crop_id=uuid.uuid4(),
            activity_type="irrigation",
            activity_date=date.today(),
            metadata={"method": "drip", "qty_L": 500},
        )
        assert a.activity_type == "irrigation"
        assert a.metadata["qty_L"] == 500

    def test_empty_activity_type_rejected(self):
        with pytest.raises(ValidationError):
            ActivityLogCreate(
                crop_id=uuid.uuid4(),
                activity_type="",
                activity_date=date.today(),
            )

    def test_optional_fields_default_none(self):
        a = ActivityLogCreate(
            crop_id=uuid.uuid4(),
            activity_type="scouting",
            activity_date=date.today(),
        )
        assert a.description is None
        assert a.performed_by is None
        assert a.metadata is None

    def test_update_partial(self):
        u = ActivityLogUpdate(performed_by="New Worker")
        assert u.performed_by == "New Worker"
        assert u.activity_type is None


# ===========================================================================
# DiseaseHistoryCreate
# ===========================================================================
class TestDiseaseHistorySchema:
    def test_valid(self):
        d = DiseaseHistoryCreate(
            crop_id=uuid.uuid4(),
            disease_name="Leaf Blast",
            severity="high",
            confidence=92.0,
            detected_date=date.today(),
            detected_by="cv_model",
        )
        assert d.disease_name == "Leaf Blast"
        assert d.confidence == 92.0

    def test_with_treatment(self):
        d = DiseaseHistoryCreate(
            crop_id=uuid.uuid4(),
            disease_name="Brown Plant Hopper",
            severity="medium",
            confidence=75.5,
            detected_date=date.today(),
            detected_by="agronomist",
            treatment_applied="Carbofuran 3G",
            treatment_date=date.today(),
        )
        assert d.treatment_applied == "Carbofuran 3G"

    def test_update_partial(self):
        u = DiseaseHistoryUpdate(status="resolved")
        assert u.status == "resolved"


# ===========================================================================
# IrrigationCreate
# ===========================================================================
class TestIrrigationSchema:
    def test_valid(self):
        i = IrrigationCreate(
            crop_id=uuid.uuid4(),
            irrigation_date=date.today(),
            method="drip",
            quantity_liters=1000.0,
        )
        assert i.quantity_liters == 1000.0

    def test_with_cost(self):
        i = IrrigationCreate(
            crop_id=uuid.uuid4(),
            irrigation_date=date.today(),
            method="flood",
            quantity_liters=5000.0,
            cost=800.0,
            water_source="canal",
        )
        assert i.water_source == "canal"

    def test_update_partial(self):
        u = IrrigationUpdate(method="sprinkler")
        assert u.method == "sprinkler"
        assert u.quantity_liters is None


# ===========================================================================
# FertilizerApplicationCreate
# ===========================================================================
class TestFertilizerSchema:
    def test_valid(self):
        f = FertilizerApplicationCreate(
            crop_id=uuid.uuid4(),
            application_date=date.today(),
            fertilizer_type="Urea",
            amount_kg_ha=50.0,
            method="broadcast",
        )
        assert f.fertilizer_type == "Urea"

    def test_with_npk_breakdown(self):
        f = FertilizerApplicationCreate(
            crop_id=uuid.uuid4(),
            application_date=date.today(),
            fertilizer_type="NPK 10:26:26",
            amount_kg_ha=100.0,
            method="fertigation",
            nitrogen_kg=10.0,
            phosphorus_kg=26.0,
            potassium_kg=26.0,
            growth_stage="flowering",
        )
        assert f.nitrogen_kg == 10.0
        assert f.growth_stage == "flowering"

    def test_update_partial(self):
        u = FertilizerApplicationUpdate(notes="Applied in evening")
        assert u.notes == "Applied in evening"
        assert u.fertilizer_type is None


# ===========================================================================
# WeatherCacheCreate
# ===========================================================================
class TestWeatherCacheSchema:
    def test_valid(self):
        w = WeatherCacheCreate(
            field_id=uuid.uuid4(),
            record_date=date.today(),
            source="openweathermap",
            temperature_min=22.0,
            temperature_max=38.0,
            temperature_avg=30.0,
            rainfall=12.5,
        )
        assert w.source == "openweathermap"
        assert w.rainfall == 12.5

    def test_with_forecast(self):
        w = WeatherCacheCreate(
            field_id=uuid.uuid4(),
            record_date=date.today(),
            source="nasa_power",
            forecast={"days": [{"date": "2025-07-14", "rain": 5.0}]},
        )
        assert w.forecast["days"][0]["rain"] == 5.0

    def test_update_partial(self):
        u = WeatherCacheUpdate(rainfall=0.0)
        assert u.rainfall == 0.0
