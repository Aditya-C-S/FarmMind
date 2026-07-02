"""
Pydantic schemas for Field model.
Handles request/response validation for field endpoints.
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from uuid import UUID
from decimal import Decimal


class FieldCreate(BaseModel):
    """
    Schema for creating a new field.
    Used in POST /fields requests.
    """
    farmer_id: UUID = Field(..., description="ID of the farmer who owns this field")
    field_name: str = Field(..., min_length=1, max_length=100, description="Name of the field")
    area_acres: Decimal = Field(..., gt=0, description="Area of field in acres")
    soil_type: Optional[str] = Field(None, max_length=50, description="Type of soil in the field")
    latitude: Optional[Decimal] = Field(None, ge=-90, le=90, description="Latitude coordinate")
    longitude: Optional[Decimal] = Field(None, ge=-180, le=180, description="Longitude coordinate")


class FieldUpdate(BaseModel):
    """
    Schema for updating an existing field.
    Used in PUT /fields/{field_id} requests.
    """
    field_name: Optional[str] = Field(None, min_length=1, max_length=100)
    area_acres: Optional[Decimal] = Field(None, gt=0)
    soil_type: Optional[str] = Field(None, max_length=50)
    latitude: Optional[Decimal] = Field(None, ge=-90, le=90)
    longitude: Optional[Decimal] = Field(None, ge=-180, le=180)


class FieldResponse(BaseModel):
    """
    Schema for field response.
    Used in GET /fields and GET /fields/{field_id} responses.
    """
    field_id: UUID
    farmer_id: UUID
    field_name: str
    area_acres: Decimal
    soil_type: Optional[str] = None
    latitude: Optional[Decimal] = None
    longitude: Optional[Decimal] = None
    
    class Config:
        from_attributes = True


class FieldDetailResponse(FieldResponse):
    """
    Extended field response with related crops.
    Includes all crops grown in this field.
    """
    crops: List['CropResponse'] = []
    
    class Config:
        from_attributes = True


# Import CropResponse for forward reference
from app.schemas.crop import CropResponse
FieldDetailResponse.model_rebuild()
