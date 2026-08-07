"""
Pydantic schemas for Irrigation model.
Handles request/response validation for irrigation endpoints.
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import date, datetime
from uuid import UUID
from decimal import Decimal


class IrrigationCreate(BaseModel):
    """Schema for creating a new irrigation record"""
    crop_id: UUID = Field(..., description="ID of the crop")
    irrigation_date: date = Field(..., description="Date of irrigation")
    method: str = Field(..., description="Method: drip, flood, sprinkler, manual, canal, etc.")
    quantity_liters: Decimal = Field(..., gt=0, description="Water quantity in liters")
    duration_hours: Optional[Decimal] = Field(None, ge=0, description="Duration in hours")
    cost: Optional[Decimal] = Field(None, ge=0, description="Cost in ₹")
    water_source: Optional[str] = Field(None, description="Source: borewell, canal, tank, etc.")
    pressure_level: Optional[str] = Field(None, description="Pressure level: low, medium, high")
    notes: Optional[str] = Field(None, max_length=500)


class IrrigationUpdate(BaseModel):
    """Schema for updating irrigation record"""
    method: Optional[str] = None
    quantity_liters: Optional[Decimal] = Field(None, gt=0)
    duration_hours: Optional[Decimal] = None
    cost: Optional[Decimal] = None
    water_source: Optional[str] = None
    pressure_level: Optional[str] = None
    notes: Optional[str] = None


class IrrigationResponse(BaseModel):
    """Schema for irrigation response"""
    irrigation_id: UUID
    crop_id: UUID
    irrigation_date: date
    method: str
    quantity_liters: Decimal
    duration_hours: Optional[Decimal] = None
    cost: Optional[Decimal] = None
    cost_per_liter: Optional[Decimal] = None
    water_source: Optional[str] = None
    pressure_level: Optional[str] = None
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class IrrigationListResponse(BaseModel):
    """Schema for listing irrigation records"""
    irrigation_id: UUID
    crop_id: UUID
    irrigation_date: date
    method: str
    quantity_liters: Decimal
    cost: Optional[Decimal] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class IrrigationStatsResponse(BaseModel):
    """Schema for irrigation statistics"""
    total_irrigation_events: int = Field(..., description="Total number of irrigation events")
    total_water_liters: Decimal = Field(..., description="Total water used in liters")
    total_cost: Decimal = Field(..., description="Total cost in ₹")
    avg_per_event_liters: Decimal = Field(..., description="Average water per event")
    avg_per_event_cost: Decimal = Field(..., description="Average cost per event")
    most_used_method: Optional[str] = Field(None, description="Most frequently used method")