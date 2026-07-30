"""
FarmMind pytest configuration.
Sets up the shared in-memory-style DB fixture using your real PostgreSQL.
Each test gets a clean transaction that is rolled back after the test.
"""

import pytest
import uuid
from datetime import date
from sqlalchemy.orm import sessionmaker

# ── Bring models into scope so create_all knows about them ──────────────────
import app.models  # noqa: F401  — registers all ORM models with metadata

from app.database.database import engine
from app.database.base     import Base


@pytest.fixture(scope="session", autouse=True)
def create_tables():
    """Create all tables once for the entire test session."""
    Base.metadata.create_all(bind=engine)
    yield
    # Tables are left intact (your real DB); data is cleaned per test via rollback.


@pytest.fixture()
def db():
    """
    Provide a database session that is rolled back after every test.
    This means no test data leaks between tests.
    """
    connection = engine.connect()
    transaction = connection.begin()
    Session = sessionmaker(bind=connection)
    session  = Session()

    yield session

    session.close()
    transaction.rollback()
    connection.close()


# ── Reusable fixtures: seeded Farmer → Field → Crop ─────────────────────────

@pytest.fixture()
def farmer(db):
    from app.models.farmer import Farmer
    f = Farmer(
        name="Pytest Farmer",
        phone="9999900000",
        email=f"pytest_{uuid.uuid4().hex[:8]}@farmmind.com",
        district="Test District",
        state="Test State",
    )
    db.add(f)
    db.flush()
    return f


@pytest.fixture()
def field(db, farmer):
    from app.models.field import Field
    fi = Field(
        farmer_id=farmer.farmer_id,
        field_name="Pytest Field",
        area_acres=5.0,
        soil_type="Loamy",
        latitude=10.0,
        longitude=79.0,
    )
    db.add(fi)
    db.flush()
    return fi


@pytest.fixture()
def crop(db, field):
    from app.models.crop import Crop
    c = Crop(
        field_id=field.field_id,
        crop_type="Rice",
        variety="IR-64",
        sowing_date=date(2025, 6, 1),
        expected_harvest_date=date(2025, 10, 1),
        status="Active",
    )
    db.add(c)
    db.flush()
    return c
