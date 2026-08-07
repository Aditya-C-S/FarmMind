"""
FarmMind Phase 2 - Quick Test Script
=====================================
Tests models, schemas, and services for Phase 2 (Farm Memory layer).
Run with: python test_phase2.py

Does NOT require pytest. Uses your real PostgreSQL DB from .env.
All test data is cleaned up after each test.
"""

import sys
import os
import traceback
from datetime import date, timedelta

# ── Make sure we run from the backend/ folder ──────────────────────────────
sys.path.insert(0, os.path.dirname(__file__))

# ── Colour helpers ──────────────────────────────────────────────────────────
GREEN  = "\033[92m"
RED    = "\033[91m"
YELLOW = "\033[93m"
CYAN   = "\033[96m"
RESET  = "\033[0m"
BOLD   = "\033[1m"

passed = []
failed = []

def ok(name: str):
    passed.append(name)
    print(f"  {GREEN}✓{RESET} {name}")

def fail(name: str, err):
    failed.append(name)
    print(f"  {RED}✗{RESET} {name}")
    print(f"    {RED}{err}{RESET}")

def section(title: str):
    print(f"\n{CYAN}{BOLD}{'─'*55}{RESET}")
    print(f"{CYAN}{BOLD}  {title}{RESET}")
    print(f"{CYAN}{BOLD}{'─'*55}{RESET}")


# ===========================================================================
# SECTION 1: Schema (Pydantic) Validation Tests
# No DB needed — pure Python validation.
# ===========================================================================
section("1. SCHEMA VALIDATION TESTS (no DB)")

# ── Schemas import ──────────────────────────────────────────────────────────
try:
    from app.schemas.farmer import FarmerCreate, FarmerUpdate, FarmerResponse
    from app.schemas.field  import FieldCreate,  FieldUpdate,  FieldResponse
    from app.schemas.crop   import CropCreate,   CropUpdate,   CropResponse, CropStatus
    from app.schemas.activity_log      import ActivityLogCreate, ActivityLogUpdate, ActivityLogResponse
    from app.schemas.disease_history   import DiseaseHistoryCreate, DiseaseHistoryUpdate
    from app.schemas.irrigation        import IrrigationCreate, IrrigationUpdate
    from app.schemas.fertilizer_application import FertilizerApplicationCreate, FertilizerApplicationUpdate
    from app.schemas.weather_cache     import WeatherCacheCreate, WeatherCacheUpdate
    ok("All schemas imported successfully")
except Exception as e:
    fail("Schema imports", e)
    print(f"\n{RED}Cannot continue without schemas. Fix import errors above.{RESET}")
    sys.exit(1)

import uuid

# ── FarmerCreate ─────────────────────────────────────────────────────────────
try:
    f = FarmerCreate(name="Ramu Farmer", phone="9876543210", district="Thanjavur", state="Tamil Nadu", email="ramu@farmmind.com")
    assert f.name == "Ramu Farmer"
    ok("FarmerCreate - valid data")
except Exception as e:
    fail("FarmerCreate - valid data", e)

try:
    FarmerCreate(name="", phone="9876543210", district="X", state="Y")
    fail("FarmerCreate - empty name should fail", "No error raised!")
except Exception:
    ok("FarmerCreate - empty name correctly rejected")

# ── FieldCreate ──────────────────────────────────────────────────────────────
try:
    _fid = uuid.uuid4()
    f2 = FieldCreate(farmer_id=_fid, field_name="North Plot", area_acres=5.5)
    assert float(f2.area_acres) == 5.5
    ok("FieldCreate - valid data")
except Exception as e:
    fail("FieldCreate - valid data", e)

# ── CropCreate date validation ────────────────────────────────────────────────
try:
    CropCreate(
        field_id=uuid.uuid4(),
        crop_type="Rice",
        sowing_date=date(2025, 1, 1),
        expected_harvest_date=date(2024, 6, 1),  # before sowing — must fail
    )
    fail("CropCreate - harvest before sowing should fail", "No error raised!")
except Exception:
    ok("CropCreate - invalid dates correctly rejected")

try:
    c = CropCreate(
        field_id=uuid.uuid4(),
        crop_type="Rice",
        variety="IR-64",
        sowing_date=date(2025, 6, 1),
        expected_harvest_date=date(2025, 10, 1),
        status=CropStatus.ACTIVE,
    )
    assert c.crop_type == "Rice"
    ok("CropCreate - valid data with status enum")
except Exception as e:
    fail("CropCreate - valid data with status enum", e)

# ── ActivityLogCreate ─────────────────────────────────────────────────────────
try:
    a = ActivityLogCreate(
        crop_id=uuid.uuid4(),
        activity_type="irrigation",
        activity_date=date.today(),
        description="Applied 500L water",
        performed_by="Farmer Ramu",
        metadata={"method": "drip", "quantity_liters": 500},
    )
    assert a.activity_type == "irrigation"
    ok("ActivityLogCreate - valid with metadata")
except Exception as e:
    fail("ActivityLogCreate - valid with metadata", e)

# ── DiseaseHistoryCreate ─────────────────────────────────────────────────────
try:
    d = DiseaseHistoryCreate(
        crop_id=uuid.uuid4(),
        disease_name="Leaf Blast",
        severity="high",
        confidence=87.5,
        detected_date=date.today(),
        detected_by="cv_model",
    )
    assert d.disease_name == "Leaf Blast"
    ok("DiseaseHistoryCreate - valid data")
except Exception as e:
    fail("DiseaseHistoryCreate - valid data", e)

# ── IrrigationCreate ─────────────────────────────────────────────────────────
try:
    i = IrrigationCreate(
        crop_id=uuid.uuid4(),
        irrigation_date=date.today(),
        method="drip",
        quantity_liters=750.0,
        duration_hours=2.5,
        cost=450.00,
        water_source="borewell",
    )
    assert i.method == "drip"
    ok("IrrigationCreate - valid data")
except Exception as e:
    fail("IrrigationCreate - valid data", e)

# ── FertilizerApplicationCreate ───────────────────────────────────────────────
try:
    fa = FertilizerApplicationCreate(
        crop_id=uuid.uuid4(),
        application_date=date.today(),
        fertilizer_type="NPK 10:26:26",
        amount_kg_ha=50.0,
        method="broadcast",
        cost=1200.00,
        growth_stage="tillering",
    )
    assert fa.fertilizer_type == "NPK 10:26:26"
    ok("FertilizerApplicationCreate - valid data")
except Exception as e:
    fail("FertilizerApplicationCreate - valid data", e)

# ── WeatherCacheCreate ────────────────────────────────────────────────────────
try:
    w = WeatherCacheCreate(
        field_id=uuid.uuid4(),
        record_date=date.today(),
        temperature_min=24.5,
        temperature_max=36.0,
        temperature_avg=30.2,
        humidity_avg=72.0,
        rainfall=0.0,
        source="openweathermap",
    )
    assert w.source == "openweathermap"
    ok("WeatherCacheCreate - valid data")
except Exception as e:
    fail("WeatherCacheCreate - valid data", e)


# ===========================================================================
# SECTION 2: Model Import Tests
# Verifies all ORM models load without error.
# ===========================================================================
section("2. MODEL IMPORT TESTS")

try:
    from app.models.farmer               import Farmer
    from app.models.field                import Field
    from app.models.crop                 import Crop
    from app.models.activity_log         import ActivityLog
    from app.models.disease_history      import DiseaseHistory
    from app.models.irrigation           import Irrigation
    from app.models.fertilizer_application import FertilizerApplication
    from app.models.weather_cache        import WeatherCache
    ok("All ORM models imported successfully")
except Exception as e:
    fail("ORM model imports", e)
    sys.exit(1)

# Verify table names
tables = {
    Farmer:                 "farmers",
    Field:                  "fields",
    Crop:                   "crops",
    ActivityLog:            "activity_logs",
    DiseaseHistory:         "disease_history",
    Irrigation:             "irrigation",
    FertilizerApplication:  "fertilizer_application",
    WeatherCache:           "weather_cache",
}
for model, expected in tables.items():
    try:
        assert model.__tablename__ == expected, f"Expected '{expected}' got '{model.__tablename__}'"
        ok(f"{model.__name__}.__tablename__ == '{expected}'")
    except Exception as e:
        fail(f"{model.__name__} table name", e)

# Verify Phase 2 relationships on Crop
try:
    rels = [r.key for r in Crop.__mapper__.relationships]
    for rel in ["activities", "disease_history", "irrigations", "fertilizers"]:
        assert rel in rels, f"Missing relationship: {rel}"
    ok("Crop has all Phase 2 relationships")
except Exception as e:
    fail("Crop Phase 2 relationships", e)

# Verify WeatherCache relationship on Field
try:
    field_rels = [r.key for r in Field.__mapper__.relationships]
    assert "weather_cache" in field_rels
    ok("Field has weather_cache relationship")
except Exception as e:
    fail("Field weather_cache relationship", e)


# ===========================================================================
# SECTION 3: Database Connection + Service Tests
# Uses your real PostgreSQL DB. Cleans up after itself.
# ===========================================================================
section("3. DATABASE & SERVICE TESTS (real PostgreSQL)")

try:
    from app.database.database import engine, test_connection
    from app.database.base     import Base
    from sqlalchemy.orm        import sessionmaker

    # Test raw connection
    assert test_connection(), "Database connection test returned False"
    ok("PostgreSQL connection alive")

    # Create tables if missing
    Base.metadata.create_all(bind=engine)
    ok("All tables created/verified via metadata.create_all")

    Session = sessionmaker(bind=engine)
    db = Session()

except Exception as e:
    fail("DB setup", e)
    print(f"\n{YELLOW}⚠ Skipping service tests (no DB). Check your .env DATABASE_URL.{RESET}")
    db = None

if db:
    try:
        from app.services.farmer_service   import FarmerService
        from app.services.field_service    import FieldService
        from app.services.crop_service     import CropService
        from app.services.activity_service import ActivityService
        ok("All service classes imported")
    except Exception as e:
        fail("Service imports", e)
        db = None

# Track created IDs for cleanup
_farmer_id = _field_id = _crop_id = _activity_id = None

if db:
    # ── FarmerService ────────────────────────────────────────────────────────
    try:
        farmer = FarmerService.create_farmer(db, FarmerCreate(
            name="Test Farmer Script",
            phone="0000000001",
            email=f"testscript_{uuid.uuid4().hex[:6]}@farmmind.com",
            district="Test District",
            state="Test State",
        ))
        _farmer_id = farmer.farmer_id
        assert farmer.farmer_id is not None
        ok(f"FarmerService.create_farmer → {farmer.farmer_id}")
    except Exception as e:
        fail("FarmerService.create_farmer", e)

    if _farmer_id:
        try:
            retrieved = FarmerService.get_farmer_by_id(db, _farmer_id)
            assert retrieved is not None
            assert retrieved.name == "Test Farmer Script"
            ok("FarmerService.get_farmer_by_id")
        except Exception as e:
            fail("FarmerService.get_farmer_by_id", e)

        try:
            count = FarmerService.count_farmers(db)
            assert count >= 1
            ok(f"FarmerService.count_farmers → {count}")
        except Exception as e:
            fail("FarmerService.count_farmers", e)

    # ── FieldService ─────────────────────────────────────────────────────────
    if _farmer_id:
        try:
            field = FieldService.create_field(db, FieldCreate(
                farmer_id=_farmer_id,
                field_name="Test Script Field",
                area_acres=3.75,
                soil_type="Loamy",
                latitude=10.123456,
                longitude=79.654321,
            ))
            _field_id = field.field_id
            assert field.field_id is not None
            ok(f"FieldService.create_field → {field.field_id}")
        except Exception as e:
            fail("FieldService.create_field", e)

        if _field_id:
            try:
                fields = FieldService.get_fields_by_farmer(db, _farmer_id)
                assert any(f.field_id == _field_id for f in fields)
                ok(f"FieldService.get_fields_by_farmer → {len(fields)} field(s)")
            except Exception as e:
                fail("FieldService.get_fields_by_farmer", e)

    # ── CropService ──────────────────────────────────────────────────────────
    if _field_id:
        try:
            crop = CropService.create_crop(db, CropCreate(
                field_id=_field_id,
                crop_type="Rice",
                variety="IR-64",
                sowing_date=date(2025, 6, 1),
                expected_harvest_date=date(2025, 10, 1),
                status=CropStatus.ACTIVE,
            ))
            _crop_id = crop.crop_id
            assert crop.crop_id is not None
            assert crop.crop_type == "Rice"
            ok(f"CropService.create_crop → {crop.crop_id}")
        except Exception as e:
            fail("CropService.create_crop", e)

        if _crop_id:
            try:
                retrieved = CropService.get_crop_by_id(db, _crop_id)
                assert retrieved is not None
                assert retrieved.variety == "IR-64"
                ok("CropService.get_crop_by_id")
            except Exception as e:
                fail("CropService.get_crop_by_id", e)

            try:
                updated = CropService.update_crop(db, _crop_id, CropUpdate(
                    status=CropStatus.HARVESTED,
                    variety="Swarna"
                ))
                assert updated.status == "Harvested"
                assert updated.variety == "Swarna"
                ok("CropService.update_crop (status + variety)")
            except Exception as e:
                fail("CropService.update_crop", e)

            try:
                crops_by_field = CropService.get_crops_by_field(db, _field_id)
                assert any(c.crop_id == _crop_id for c in crops_by_field)
                ok(f"CropService.get_crops_by_field → {len(crops_by_field)} crop(s)")
            except Exception as e:
                fail("CropService.get_crops_by_field", e)

            try:
                crops_by_farmer = CropService.get_crops_by_farmer(db, _farmer_id)
                assert any(c.crop_id == _crop_id for c in crops_by_farmer)
                ok(f"CropService.get_crops_by_farmer → {len(crops_by_farmer)} crop(s)")
            except Exception as e:
                fail("CropService.get_crops_by_farmer", e)

    # ── ActivityService ──────────────────────────────────────────────────────
    if _crop_id:
        try:
            activity = ActivityService.create_activity(db, ActivityLogCreate(
                crop_id=_crop_id,
                activity_type="pesticide",
                activity_date=date.today(),
                description="Applied Cartap 1kg/ha",
                performed_by="Test Worker",
                metadata={"pesticide": "Cartap", "dosage": "1kg/ha"},
            ))
            _activity_id = activity.activity_id
            assert activity.activity_id is not None
            ok(f"ActivityService.create_activity → {activity.activity_id}")
        except Exception as e:
            fail("ActivityService.create_activity", e)

        if _activity_id:
            try:
                retrieved = ActivityService.get_activity_by_id(db, _activity_id)
                assert retrieved is not None
                assert retrieved.activity_type == "pesticide"
                ok("ActivityService.get_activity_by_id")
            except Exception as e:
                fail("ActivityService.get_activity_by_id", e)

            try:
                activities = ActivityService.get_activities_by_crop(db, _crop_id)
                assert len(activities) >= 1
                ok(f"ActivityService.get_activities_by_crop → {len(activities)} activity(ies)")
            except Exception as e:
                fail("ActivityService.get_activities_by_crop", e)

            try:
                count = ActivityService.count_activities_by_crop(db, _crop_id)
                assert count >= 1
                ok(f"ActivityService.count_activities_by_crop → {count}")
            except Exception as e:
                fail("ActivityService.count_activities_by_crop", e)

            try:
                updated = ActivityService.update_activity(db, _activity_id, ActivityLogUpdate(
                    description="Updated: Applied Cartap + neem oil"
                ))
                assert "Updated" in updated.description
                ok("ActivityService.update_activity")
            except Exception as e:
                fail("ActivityService.update_activity", e)

            try:
                result = ActivityService.delete_activity(db, _activity_id)
                assert result is True
                ok("ActivityService.delete_activity")
                _activity_id = None
            except Exception as e:
                fail("ActivityService.delete_activity", e)

        # Verify not found returns None / False
        try:
            ghost = ActivityService.get_activity_by_id(db, uuid.uuid4())
            assert ghost is None
            ok("ActivityService.get_activity_by_id → None for unknown ID")
        except Exception as e:
            fail("ActivityService.get_activity_by_id (not found)", e)

    # ── CropService - invalid field (negative test) ──────────────────────────
    try:
        CropService.create_crop(db, CropCreate(
            field_id=uuid.uuid4(),  # non-existent
            crop_type="Wheat",
            sowing_date=date(2025, 1, 1),
            expected_harvest_date=date(2025, 6, 1),
        ))
        fail("CropService - non-existent field should raise ValueError", "No error raised!")
    except ValueError:
        ok("CropService.create_crop → ValueError for non-existent field")
    except Exception as e:
        fail("CropService - non-existent field error type", e)

    # ── Cleanup ──────────────────────────────────────────────────────────────
    section("CLEANUP")
    try:
        if _crop_id:
            CropService.delete_crop(db, _crop_id)
            ok(f"Crop {_crop_id} deleted")
        if _field_id:
            FieldService.delete_field(db, _field_id)
            ok(f"Field {_field_id} deleted")
        if _farmer_id:
            FarmerService.delete_farmer(db, _farmer_id)
            ok(f"Farmer {_farmer_id} deleted")
    except Exception as e:
        fail("Cleanup", e)
    finally:
        db.close()


# ===========================================================================
# SUMMARY
# ===========================================================================
total = len(passed) + len(failed)
section("RESULTS")
print(f"\n  {GREEN}{BOLD}{len(passed)}/{total} tests passed{RESET}")

if failed:
    print(f"\n  {RED}{BOLD}Failed tests:{RESET}")
    for name in failed:
        print(f"    {RED}✗ {name}{RESET}")
    print()
    sys.exit(1)
else:
    print(f"\n  {GREEN}{BOLD}🎉 All tests passed!{RESET}\n")
    sys.exit(0)
