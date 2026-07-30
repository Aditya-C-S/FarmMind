"""
FarmMind - Database Reset Script
WARNING: THIS WILL DROP ALL TABLES AND RECREATE THEM.
Run this only if your database schema is out of sync with your models
(e.g. after adding new columns like 'email', 'latitude', 'longitude').
"""

import sys
import os
import logging

# Ensure we can import from app
sys.path.insert(0, os.path.dirname(__file__))

from app.database.database import engine
from app.database.base import Base

# Import all models so they are registered with Base.metadata
import app.models

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def reset_database():
    confirm = input("⚠️ WARNING: This will DROP all tables and delete all data. Are you sure? (y/n): ")
    if confirm.lower() != 'y':
        print("Cancelled.")
        return

    logger.info("Dropping all tables...")
    Base.metadata.drop_all(bind=engine)
    logger.info("✓ Tables dropped successfully")

    logger.info("Recreating all tables from current models...")
    Base.metadata.create_all(bind=engine)
    logger.info("✓ Tables created successfully")
    
    print("\n✅ Database has been successfully reset to match your current models.")

if __name__ == "__main__":
    reset_database()
