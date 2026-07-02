from app.database import engine, test_connection
from app.core.config import settings

print(f"Database URL: {settings.DATABASE_URL}")
print(f"Testing connection...")
result = test_connection()
print(f"Connection successful: {result}")