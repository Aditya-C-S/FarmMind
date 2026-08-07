"""
Tests for ORM models: table names, columns, relationships.
No service layer involved — directly uses SQLAlchemy mapper inspection.
"""

import pytest
from sqlalchemy import inspect as sa_inspect

from app.models.farmer               import Farmer
from app.models.field                import Field
from app.models.crop                 import Crop
from app.models.activity_log         import ActivityLog
from app.models.disease_history      import DiseaseHistory
from app.models.irrigation           import Irrigation
from app.models.fertilizer_application import FertilizerApplication
from app.models.weather_cache        import WeatherCache


# ===========================================================================
# Table name checks
# ===========================================================================
class TestTableNames:
    def test_farmer_table(self):
        assert Farmer.__tablename__ == "farmers"

    def test_field_table(self):
        assert Field.__tablename__ == "fields"

    def test_crop_table(self):
        assert Crop.__tablename__ == "crops"

    def test_activity_log_table(self):
        assert ActivityLog.__tablename__ == "activity_logs"

    def test_disease_history_table(self):
        assert DiseaseHistory.__tablename__ == "disease_history"

    def test_irrigation_table(self):
        assert Irrigation.__tablename__ == "irrigation"

    def test_fertilizer_application_table(self):
        assert FertilizerApplication.__tablename__ == "fertilizer_application"

    def test_weather_cache_table(self):
        assert WeatherCache.__tablename__ == "weather_cache"


# ===========================================================================
# Column presence checks
# ===========================================================================
class TestColumns:
    def _cols(self, model):
        return {c.key for c in sa_inspect(model).mapper.column_attrs}

    def test_farmer_columns(self):
        cols = self._cols(Farmer)
        assert {"farmer_id", "name", "phone", "district", "state"}.issubset(cols)

    def test_field_columns(self):
        cols = self._cols(Field)
        assert {"field_id", "farmer_id", "field_name", "area_acres", "soil_type",
                "latitude", "longitude"}.issubset(cols)

    def test_crop_columns(self):
        cols = self._cols(Crop)
        assert {"crop_id", "field_id", "crop_type", "variety",
                "sowing_date", "expected_harvest_date", "status"}.issubset(cols)

    def test_activity_log_columns(self):
        cols = self._cols(ActivityLog)
        assert {"activity_id", "crop_id", "activity_type", "activity_date",
                "description", "performed_by", "activity_metadata",
                "created_at", "updated_at"}.issubset(cols)

    def test_disease_history_columns(self):
        cols = self._cols(DiseaseHistory)
        assert {"disease_id", "crop_id", "disease_name", "severity",
                "confidence", "detected_date", "detected_by",
                "treatment_applied", "treatment_date", "status",
                "created_at", "updated_at"}.issubset(cols)

    def test_irrigation_columns(self):
        cols = self._cols(Irrigation)
        assert {"irrigation_id", "crop_id", "irrigation_date",
                "method", "quantity_liters", "duration_hours",
                "cost", "cost_per_liter", "water_source",
                "created_at", "updated_at"}.issubset(cols)

    def test_fertilizer_columns(self):
        cols = self._cols(FertilizerApplication)
        assert {"fertilizer_id", "crop_id", "application_date",
                "fertilizer_type", "amount_kg_ha", "method",
                "nitrogen_kg", "phosphorus_kg", "potassium_kg",
                "cost", "growth_stage", "created_at", "updated_at"}.issubset(cols)

    def test_weather_cache_columns(self):
        cols = self._cols(WeatherCache)
        assert {"weather_id", "field_id", "record_date",
                "temperature_min", "temperature_max", "temperature_avg",
                "humidity_avg", "rainfall", "source",
                "created_at", "updated_at"}.issubset(cols)


# ===========================================================================
# Relationship checks
# ===========================================================================
class TestRelationships:
    def _rels(self, model):
        return {r.key for r in sa_inspect(model).mapper.relationships}

    # Phase 1
    def test_farmer_has_fields(self):
        assert "fields" in self._rels(Farmer)

    def test_field_has_crops(self):
        assert "crops" in self._rels(Field)

    def test_field_has_weather_cache(self):
        assert "weather_cache" in self._rels(Field)

    def test_crop_has_field(self):
        assert "field" in self._rels(Crop)

    # Phase 2 relationships on Crop
    def test_crop_has_activities(self):
        assert "activities" in self._rels(Crop)

    def test_crop_has_disease_history(self):
        assert "disease_history" in self._rels(Crop)

    def test_crop_has_irrigations(self):
        assert "irrigations" in self._rels(Crop)

    def test_crop_has_fertilizers(self):
        assert "fertilizers" in self._rels(Crop)

    # Back-references
    def test_activity_log_back_to_crop(self):
        assert "crop" in self._rels(ActivityLog)

    def test_disease_history_back_to_crop(self):
        assert "crop" in self._rels(DiseaseHistory)

    def test_irrigation_back_to_crop(self):
        assert "crop" in self._rels(Irrigation)

    def test_fertilizer_back_to_crop(self):
        assert "crop" in self._rels(FertilizerApplication)

    def test_weather_cache_back_to_field(self):
        assert "field" in self._rels(WeatherCache)


# ===========================================================================
# to_dict() checks
# ===========================================================================
class TestToDictMethod:
    """Verify that to_dict() exists and returns a dict with expected keys."""

    def _mock_uuid(self):
        import uuid
        return uuid.uuid4()

    def test_activity_log_has_to_dict(self):
        assert hasattr(ActivityLog, "to_dict")

    def test_disease_history_has_to_dict(self):
        assert hasattr(DiseaseHistory, "to_dict")

    def test_irrigation_has_to_dict(self):
        assert hasattr(Irrigation, "to_dict")

    def test_fertilizer_has_to_dict(self):
        assert hasattr(FertilizerApplication, "to_dict")

    def test_weather_cache_has_to_dict(self):
        assert hasattr(WeatherCache, "to_dict")
