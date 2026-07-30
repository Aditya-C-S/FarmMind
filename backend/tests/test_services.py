"""
Tests for all service classes.
Uses the `db` fixture from conftest.py (rolled back after each test).
Uses the `farmer`, `field`, `crop` fixtures as pre-seeded data.
"""

import pytest
import uuid
from datetime import date

from app.services.farmer_service   import FarmerService
from app.services.field_service    import FieldService
from app.services.crop_service     import CropService
from app.services.activity_service import ActivityService

from app.schemas.farmer       import FarmerCreate, FarmerUpdate
from app.schemas.field        import FieldCreate,  FieldUpdate
from app.schemas.crop         import CropCreate,   CropUpdate, CropStatus
from app.schemas.activity_log import ActivityLogCreate, ActivityLogUpdate


# ===========================================================================
# FarmerService
# ===========================================================================
class TestFarmerService:

    def test_create_farmer(self, db):
        farmer = FarmerService.create_farmer(db, FarmerCreate(
            name="Ramu",
            phone="9999900001",
            email=f"ramu_{uuid.uuid4().hex[:6]}@test.com",
            district="Thanjavur",
            state="Tamil Nadu",
        ))
        assert farmer.farmer_id is not None
        assert farmer.name == "Ramu"
        assert farmer.district == "Thanjavur"

    def test_get_farmer_by_id(self, db, farmer):
        retrieved = FarmerService.get_farmer_by_id(db, farmer.farmer_id)
        assert retrieved is not None
        assert retrieved.farmer_id == farmer.farmer_id
        assert retrieved.name == farmer.name

    def test_get_farmer_by_id_not_found(self, db):
        result = FarmerService.get_farmer_by_id(db, uuid.uuid4())
        assert result is None

    def test_get_farmer_by_email(self, db, farmer):
        retrieved = FarmerService.get_farmer_by_email(db, farmer.email)
        assert retrieved is not None
        assert retrieved.farmer_id == farmer.farmer_id

    def test_get_all_farmers(self, db, farmer):
        farmers = FarmerService.get_all_farmers(db)
        assert any(f.farmer_id == farmer.farmer_id for f in farmers)

    def test_update_farmer(self, db, farmer):
        updated = FarmerService.update_farmer(db, farmer.farmer_id, FarmerUpdate(
            district="Chennai",
            state="Tamil Nadu",
        ))
        assert updated is not None
        assert updated.district == "Chennai"

    def test_update_farmer_not_found(self, db):
        result = FarmerService.update_farmer(db, uuid.uuid4(), FarmerUpdate(district="X"))
        assert result is None

    def test_delete_farmer(self, db):
        from app.models.farmer import Farmer
        f = Farmer(
            name="Delete Me",
            phone="0000000099",
            email=f"delete_{uuid.uuid4().hex[:6]}@test.com",
            district="D",
            state="S",
        )
        db.add(f)
        db.flush()
        result = FarmerService.delete_farmer(db, f.farmer_id)
        assert result is True
        assert FarmerService.get_farmer_by_id(db, f.farmer_id) is None

    def test_delete_farmer_not_found(self, db):
        result = FarmerService.delete_farmer(db, uuid.uuid4())
        assert result is False

    def test_count_farmers(self, db, farmer):
        count = FarmerService.count_farmers(db)
        assert count >= 1


# ===========================================================================
# FieldService
# ===========================================================================
class TestFieldService:

    def test_create_field(self, db, farmer):
        f = FieldService.create_field(db, FieldCreate(
            farmer_id=farmer.farmer_id,
            field_name="South Plot",
            area_acres=4.5,
            soil_type="Black Cotton",
            latitude=10.5,
            longitude=79.5,
        ))
        assert f.field_id is not None
        assert f.field_name == "South Plot"
        assert f.farmer_id == farmer.farmer_id

    def test_create_field_nonexistent_farmer(self, db):
        with pytest.raises(ValueError, match="not found"):
            FieldService.create_field(db, FieldCreate(
                farmer_id=uuid.uuid4(),
                field_name="Ghost Field",
                area_acres=1.0,
            ))

    def test_get_field_by_id(self, db, field):
        result = FieldService.get_field_by_id(db, field.field_id)
        assert result is not None
        assert result.field_id == field.field_id

    def test_get_field_by_id_not_found(self, db):
        assert FieldService.get_field_by_id(db, uuid.uuid4()) is None

    def test_get_fields_by_farmer(self, db, field, farmer):
        fields = FieldService.get_fields_by_farmer(db, farmer.farmer_id)
        assert any(f.field_id == field.field_id for f in fields)

    def test_get_all_fields(self, db, field):
        fields = FieldService.get_all_fields(db)
        assert any(f.field_id == field.field_id for f in fields)

    def test_update_field(self, db, field):
        updated = FieldService.update_field(db, field.field_id, FieldUpdate(
            field_name="Updated Plot",
            area_acres=6.0,
        ))
        assert updated is not None
        assert updated.field_name == "Updated Plot"
        assert float(updated.area_acres) == 6.0

    def test_update_field_not_found(self, db):
        result = FieldService.update_field(db, uuid.uuid4(), FieldUpdate(field_name="X"))
        assert result is None

    def test_delete_field(self, db, farmer):
        from app.models.field import Field
        f = Field(farmer_id=farmer.farmer_id, field_name="Temp", area_acres=1.0)
        db.add(f)
        db.flush()
        assert FieldService.delete_field(db, f.field_id) is True
        assert FieldService.get_field_by_id(db, f.field_id) is None

    def test_delete_field_not_found(self, db):
        assert FieldService.delete_field(db, uuid.uuid4()) is False

    def test_count_fields(self, db, field, farmer):
        total = FieldService.count_fields(db)
        by_farmer = FieldService.count_fields(db, farmer_id=farmer.farmer_id)
        assert total >= 1
        assert by_farmer >= 1


# ===========================================================================
# CropService
# ===========================================================================
class TestCropService:

    def test_create_crop(self, db, field):
        c = CropService.create_crop(db, CropCreate(
            field_id=field.field_id,
            crop_type="Tomato",
            variety="Arka Samrat",
            sowing_date=date(2025, 3, 1),
            expected_harvest_date=date(2025, 7, 1),
            status=CropStatus.ACTIVE,
        ))
        assert c.crop_id is not None
        assert c.crop_type == "Tomato"
        assert c.variety == "Arka Samrat"

    def test_create_crop_nonexistent_field(self, db):
        with pytest.raises(ValueError, match="not found"):
            CropService.create_crop(db, CropCreate(
                field_id=uuid.uuid4(),
                crop_type="Rice",
                sowing_date=date(2025, 1, 1),
                expected_harvest_date=date(2025, 6, 1),
            ))

    def test_create_crop_invalid_dates(self, db, field):
        """Service-level date check (schema also blocks this, double safety)."""
        with pytest.raises((ValueError, Exception)):
            CropService.create_crop(db, CropCreate(
                field_id=field.field_id,
                crop_type="Rice",
                sowing_date=date(2025, 10, 1),
                expected_harvest_date=date(2025, 1, 1),
            ))

    def test_get_crop_by_id(self, db, crop):
        result = CropService.get_crop_by_id(db, crop.crop_id)
        assert result is not None
        assert result.crop_id == crop.crop_id
        assert result.crop_type == crop.crop_type

    def test_get_crop_by_id_not_found(self, db):
        assert CropService.get_crop_by_id(db, uuid.uuid4()) is None

    def test_get_crops_by_field(self, db, crop, field):
        crops = CropService.get_crops_by_field(db, field.field_id)
        assert any(c.crop_id == crop.crop_id for c in crops)

    def test_get_crops_by_farmer(self, db, crop, farmer):
        crops = CropService.get_crops_by_farmer(db, farmer.farmer_id)
        assert any(c.crop_id == crop.crop_id for c in crops)

    def test_get_crops_by_type(self, db, crop):
        crops = CropService.get_crops_by_type(db, crop.crop_type)
        assert any(c.crop_id == crop.crop_id for c in crops)

    def test_get_all_crops(self, db, crop):
        all_crops = CropService.get_all_crops(db)
        assert any(c.crop_id == crop.crop_id for c in all_crops)

    def test_update_crop_status(self, db, crop):
        updated = CropService.update_crop(db, crop.crop_id, CropUpdate(
            status=CropStatus.HARVESTED
        ))
        assert updated is not None
        assert updated.status == "Harvested"

    def test_update_crop_variety(self, db, crop):
        updated = CropService.update_crop(db, crop.crop_id, CropUpdate(variety="Swarna"))
        assert updated.variety == "Swarna"

    def test_update_crop_not_found(self, db):
        result = CropService.update_crop(db, uuid.uuid4(), CropUpdate(variety="X"))
        assert result is None

    def test_delete_crop(self, db, field):
        from app.models.crop import Crop
        c = Crop(
            field_id=field.field_id,
            crop_type="Wheat",
            sowing_date=date(2025, 1, 1),
            expected_harvest_date=date(2025, 5, 1),
            status="Active",
        )
        db.add(c)
        db.flush()
        assert CropService.delete_crop(db, c.crop_id) is True
        assert CropService.get_crop_by_id(db, c.crop_id) is None

    def test_delete_crop_not_found(self, db):
        assert CropService.delete_crop(db, uuid.uuid4()) is False

    def test_count_crops(self, db, crop, field, farmer):
        total = CropService.count_crops(db)
        by_field = CropService.count_crops(db, field_id=field.field_id)
        by_farmer = CropService.count_crops(db, farmer_id=farmer.farmer_id)
        assert total >= 1
        assert by_field >= 1
        assert by_farmer >= 1


# ===========================================================================
# ActivityService
# ===========================================================================
class TestActivityService:

    def test_create_activity(self, db, crop):
        a = ActivityService.create_activity(db, ActivityLogCreate(
            crop_id=crop.crop_id,
            activity_type="fertilizer",
            activity_date=date.today(),
            description="Applied Urea 50kg/ha",
            performed_by="Field Worker",
            metadata={"type": "Urea", "kg_ha": 50},
        ))
        assert a.activity_id is not None
        assert a.activity_type == "fertilizer"
        assert a.metadata["kg_ha"] == 50

    def test_create_activity_nonexistent_crop(self, db):
        with pytest.raises(ValueError, match="not found"):
            ActivityService.create_activity(db, ActivityLogCreate(
                crop_id=uuid.uuid4(),
                activity_type="scouting",
                activity_date=date.today(),
            ))

    def test_get_activity_by_id(self, db, crop):
        from app.models.activity_log import ActivityLog
        a = ActivityLog(
            crop_id=crop.crop_id,
            activity_type="pesticide",
            activity_date=date.today(),
        )
        db.add(a)
        db.flush()
        result = ActivityService.get_activity_by_id(db, a.activity_id)
        assert result is not None
        assert result.activity_id == a.activity_id

    def test_get_activity_by_id_not_found(self, db):
        assert ActivityService.get_activity_by_id(db, uuid.uuid4()) is None

    def test_get_activities_by_crop(self, db, crop):
        from app.models.activity_log import ActivityLog
        a1 = ActivityLog(crop_id=crop.crop_id, activity_type="irrigation", activity_date=date.today())
        a2 = ActivityLog(crop_id=crop.crop_id, activity_type="weeding",    activity_date=date.today())
        db.add_all([a1, a2])
        db.flush()
        activities = ActivityService.get_activities_by_crop(db, crop.crop_id)
        ids = {a.activity_id for a in activities}
        assert a1.activity_id in ids
        assert a2.activity_id in ids

    def test_get_activities_by_type(self, db, crop):
        from app.models.activity_log import ActivityLog
        a = ActivityLog(crop_id=crop.crop_id, activity_type="harvest", activity_date=date.today())
        db.add(a)
        db.flush()
        results = ActivityService.get_activities_by_type(db, crop.crop_id, "harvest")
        assert any(r.activity_id == a.activity_id for r in results)

    def test_get_activities_by_date_range(self, db, crop):
        from app.models.activity_log import ActivityLog
        today = date.today()
        a = ActivityLog(crop_id=crop.crop_id, activity_type="soil_test", activity_date=today)
        db.add(a)
        db.flush()
        results = ActivityService.get_activities_by_date_range(
            db, crop.crop_id,
            start_date=today,
            end_date=today,
        )
        assert any(r.activity_id == a.activity_id for r in results)

    def test_update_activity(self, db, crop):
        from app.models.activity_log import ActivityLog
        a = ActivityLog(crop_id=crop.crop_id, activity_type="scouting", activity_date=date.today())
        db.add(a)
        db.flush()

        updated = ActivityService.update_activity(db, a.activity_id, ActivityLogUpdate(
            description="Observed early signs of pest",
            performed_by="Scout Team",
        ))
        assert updated is not None
        assert updated.description == "Observed early signs of pest"
        assert updated.performed_by == "Scout Team"

    def test_update_activity_not_found(self, db):
        result = ActivityService.update_activity(
            db, uuid.uuid4(), ActivityLogUpdate(description="X")
        )
        assert result is None

    def test_delete_activity(self, db, crop):
        from app.models.activity_log import ActivityLog
        a = ActivityLog(crop_id=crop.crop_id, activity_type="pruning", activity_date=date.today())
        db.add(a)
        db.flush()
        assert ActivityService.delete_activity(db, a.activity_id) is True
        assert ActivityService.get_activity_by_id(db, a.activity_id) is None

    def test_delete_activity_not_found(self, db):
        assert ActivityService.delete_activity(db, uuid.uuid4()) is False

    def test_count_activities_by_crop(self, db, crop):
        from app.models.activity_log import ActivityLog
        a1 = ActivityLog(crop_id=crop.crop_id, activity_type="irrigation", activity_date=date.today())
        a2 = ActivityLog(crop_id=crop.crop_id, activity_type="weeding",    activity_date=date.today())
        db.add_all([a1, a2])
        db.flush()
        count = ActivityService.count_activities_by_crop(db, crop.crop_id)
        assert count >= 2
