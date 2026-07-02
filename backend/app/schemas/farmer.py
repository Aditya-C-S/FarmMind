"""
Pydantic schemas for Farmer model.
Handles request/response validation for farmer endpoints.
"""

from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime
from uuid import UUID


class FarmerCreate(BaseModel):
    """
    Schema for creating a new farmer.
    Used in POST /farmers requests.
    """
    name: str = Field(..., min_length=1, max_length=100, description="Farmer's full name")
    phone: str = Field(..., min_length=10, max_length=15, description="Farmer's phone number")
    email: EmailStr = Field(..., description="Farmer's email address (must be unique)")
    district: str = Field(..., min_length=1, max_length=50, description="District name")
    state: str = Field(..., min_length=1, max_length=50, description="State name")


class FarmerUpdate(BaseModel):
    """
    Schema for updating an existing farmer.
    Used in PUT /farmers/{farmer_id} requests.
    """
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    phone: Optional[str] = Field(None, min_length=10, max_length=15)
    email: Optional[EmailStr] = None
    district: Optional[str] = Field(None, min_length=1, max_length=50)
    state: Optional[str] = Field(None, min_length=1, max_length=50)


class FarmerResponse(BaseModel):
    """
    Schema for farmer response.
    Used in GET /farmers and GET /farmers/{farmer_id} responses.
    """
    farmer_id: UUID
    name: str
    phone: str
    email: str
    district: str
    state: str
    created_at: datetime
    
    class Config:
        from_attributes = True  # Pydantic v2: allows reading from ORM models


class FarmerDetailResponse(FarmerResponse):
    """
    Extended farmer response with related fields.
    Includes farmer's fields information.
    """
    fields: List['FieldResponse'] = []
    
    class Config:
        from_attributes = True


# Import FieldResponse for forward reference
from app.schemas.field import FieldResponse
FarmerDetailResponse.model_rebuild()
