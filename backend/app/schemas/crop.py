"""
Pydantic schemas for Crop model.
Handles request/response validation for crop endpoints.
"""

from pydantic import BaseModel, Field, field_validator
from typing import Optional
from uuid import UUID
from datetime import date
from enum import Enum


class CropStatus(str, Enum):
    """Valid statuses for a crop."""
    ACTIVE = "Active"
    HARVESTED = "Harvested"
    FAILED = "Failed"


class CropCreate(BaseModel):
    """
    Schema for creating a new crop.
    Used in POST /crops requests.
    """
    field_id: UUID = Field(..., description="ID of the field where crop will be grown")
    crop_type: str = Field(..., min_length=1, max_length=50, description="Type of crop (e.g., Rice, Tomato)")
    variety: Optional[str] = Field(None, max_length=100, description="Variety of crop (e.g., IR-64, Arka Samrat)")
    sowing_date: date = Field(..., description="Date when crop was/will be sown")
    expected_harvest_date: date = Field(..., description="Expected harvest date")
    status: CropStatus = Field(CropStatus.ACTIVE, description="Crop status (Active, Harvested, Failed)")
    
    @field_validator('expected_harvest_date')
    @classmethod
    def validate_harvest_date(cls, v, info):
        """Ensure harvest date is after sowing date"""
        if 'sowing_date' in info.data:
            if v <= info.data['sowing_date']:
                raise ValueError('Expected harvest date must be after sowing date')
        return v


class CropUpdate(BaseModel):
    """
    Schema for updating an existing crop.
    Used in PUT /crops/{crop_id} requests.
    """
    crop_type: Optional[str] = Field(None, min_length=1, max_length=50)
    variety: Optional[str] = Field(None, max_length=100)
    sowing_date: Optional[date] = None
    expected_harvest_date: Optional[date] = None
    status: Optional[CropStatus] = Field(None, description="Crop status (Active, Harvested, Failed)")
    
    @field_validator('expected_harvest_date')
    @classmethod
    def validate_harvest_date(cls, v, info):
        """Ensure harvest date is after sowing date if both are provided"""
        if v and 'sowing_date' in info.data and info.data['sowing_date']:
            if v <= info.data['sowing_date']:
                raise ValueError('Expected harvest date must be after sowing date')
        return v


class CropResponse(BaseModel):
    """
    Schema for crop response.
    Used in GET /crops and GET /crops/{crop_id} responses.
    """
    crop_id: UUID
    field_id: UUID
    crop_type: str
    variety: Optional[str] = None
    sowing_date: date
    expected_harvest_date: date
    status: CropStatus
    
    class Config:
        from_attributes = True


class CropDetailResponse(CropResponse):
    """
    Extended crop response with field information.
    """
    field: Optional['FieldResponse'] = None
    
    class Config:
        from_attributes = True


# Import FieldResponse for forward reference
from app.schemas.field import FieldResponse
CropDetailResponse.model_rebuild()
