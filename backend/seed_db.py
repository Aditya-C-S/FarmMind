import sys
import os
import uuid
import logging
from datetime import date, timedelta

# Ensure we can import from app
sys.path.insert(0, os.path.dirname(__file__))

from app.database.database import SessionLocal
from app.models.farmer import Farmer
from app.models.field import Field
from app.models.crop import Crop
from app.models.activity_log import ActivityLog

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def seed_database():
    db = SessionLocal()
    try:
        # Create a Farmer
        farmer = Farmer(
            name="John Doe",
            phone="1234567890",
            email="john.doe@example.com",
            district="Bangalore",
            state="Karnataka"
        )
        db.add(farmer)
        db.commit()
        db.refresh(farmer)
        logger.info(f"Created Farmer: {farmer.name} (ID: {farmer.farmer_id})")

        # Create a Field (in Bangalore so Weather API has a real location)
        field = Field(
            farmer_id=farmer.farmer_id,
            field_name="North Field",
            area_acres=5.0,
            soil_type="Clay Loam",
            latitude=12.9716,
            longitude=77.5946
        )
        db.add(field)
        db.commit()
        db.refresh(field)
        logger.info(f"Created Field: {field.field_name} (ID: {field.field_id})")

        # Create Crop 1 (Rice, sown 30 days ago -> likely 'Tillering' stage)
        rice_sowing_date = date.today() - timedelta(days=30)
        rice_harvest_date = rice_sowing_date + timedelta(days=120)
        
        rice_crop = Crop(
            field_id=field.field_id,
            crop_type="rice",
            variety="IR-64",
            sowing_date=rice_sowing_date,
            expected_harvest_date=rice_harvest_date,
            status="active"
        )
        db.add(rice_crop)
        db.commit()
        db.refresh(rice_crop)
        logger.info(f"Created Crop: {rice_crop.crop_type} (ID: {rice_crop.crop_id})")

        # Create Crop 2 (Tomato, sown 10 days ago -> likely early stage)
        tomato_sowing_date = date.today() - timedelta(days=10)
        tomato_harvest_date = tomato_sowing_date + timedelta(days=90)
        
        tomato_crop = Crop(
            field_id=field.field_id,
            crop_type="tomato",
            variety="Arka Samrat",
            sowing_date=tomato_sowing_date,
            expected_harvest_date=tomato_harvest_date,
            status="active"
        )
        db.add(tomato_crop)
        db.commit()
        db.refresh(tomato_crop)
        logger.info(f"Created Crop: {tomato_crop.crop_type} (ID: {tomato_crop.crop_id})")

        # Add Activity Logs for Rice so Context Fusion has Activity context
        # 1. Weeding
        weed_activity = ActivityLog(
            crop_id=rice_crop.crop_id,
            activity_type="weeding",
            activity_date=date.today() - timedelta(days=5),
            description="Manual weeding in the north sector",
            performed_by="John Doe"
        )
        # 2. Fertilizer
        fert_activity = ActivityLog(
            crop_id=rice_crop.crop_id,
            activity_type="fertilizer",
            activity_date=date.today() - timedelta(days=2),
            description="Applied NPK",
            performed_by="John Doe",
            activity_metadata={"type": "NPK", "amount_kg": 50}
        )
        db.add(weed_activity)
        db.add(fert_activity)
        db.commit()
        logger.info(f"Added Activity Logs for crop: {rice_crop.crop_id}")

        print("\n✅ Database has been successfully seeded with test data.")
        print(f"\n--- USE THESE IDs IN THE DASHBOARD ---")
        print(f"Rice Crop ID:   {rice_crop.crop_id}")
        print(f"Tomato Crop ID: {tomato_crop.crop_id}")
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error seeding database: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()
