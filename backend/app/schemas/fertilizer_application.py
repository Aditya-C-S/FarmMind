"""
Pydantic schemas for Fertilizer Application model.
Handles request/response validation for fertilizer endpoints.
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import date, datetime
from uuid import UUID
from decimal import Decimal


class FertilizerApplicationCreate(BaseModel):
    """Schema for creating a new fertilizer application record"""
    crop_id: UUID = Field(..., description="ID of the crop")
    application_date: date = Field(..., description="Date of application")
    fertilizer_type: str = Field(..., min_length=1, max_length=100, description="Type of fertilizer")
    nitrogen_kg: Optional[Decimal] = Field(None, ge=0, description="Nitrogen amount in kg")
    phosphorus_kg: Optional[Decimal] = Field(None, ge=0, description="Phosphorus amount in kg")
    potassium_kg: Optional[Decimal] = Field(None, ge=0, description="Potassium amount in kg")
    amount_kg_ha: Decimal = Field(..., gt=0, description="Amount per hectare in kg")
    amount_total_kg: Optional[Decimal] = Field(None, gt=0, description="Total amount in kg")
    method: str = Field(..., description="Method: broadcast, fertigation, foliar, soil_application")
    cost: Optional[Decimal] = Field(None, ge=0, description="Cost in ₹")
    growth_stage: Optional[str] = Field(None, description="Growth stage: nursery, tillering, flowering, etc.")
    brand: Optional[str] = Field(None, max_length=100)
    batch_number: Optional[str] = Field(None, max_length=50)
    weather_conditions: Optional[str] = Field(None, max_length=100)
    notes: Optional[str] = Field(None, max_length=500)


class FertilizerApplicationUpdate(BaseModel):
    """Schema for updating fertilizer application record"""
    fertilizer_type: Optional[str] = None
    nitrogen_kg: Optional[Decimal] = None
    phosphorus_kg: Optional[Decimal] = None
    potassium_kg: Optional[Decimal] = None
    amount_kg_ha: Optional[Decimal] = None
    amount_total_kg: Optional[Decimal] = None
    method: Optional[str] = None
    cost: Optional[Decimal] = None
    growth_stage: Optional[str] = None
    brand: Optional[str] = None
    batch_number: Optional[str] = None
    weather_conditions: Optional[str] = None
    notes: Optional[str] = None


class FertilizerApplicationResponse(BaseModel):
    """Schema for fertilizer application response"""
    fertilizer_id: UUID
    crop_id: UUID
    application_date: date
    fertilizer_type: str
    nitrogen_kg: Optional[Decimal] = None
    phosphorus_kg: Optional[Decimal] = None
    potassium_kg: Optional[Decimal] = None
    amount_kg_ha: Decimal
    amount_total_kg: Optional[Decimal] = None
    method: str
    cost: Optional[Decimal] = None
    cost_per_kg: Optional[Decimal] = None
    growth_stage: Optional[str] = None
    brand: Optional[str] = None
    batch_number: Optional[str] = None
    weather_conditions: Optional[str] = None
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class FertilizerApplicationListResponse(BaseModel):
    """Schema for listing fertilizer applications"""
    fertilizer_id: UUID
    crop_id: UUID
    application_date: date
    fertilizer_type: str
    amount_kg_ha: Decimal
    method: str
    cost: Optional[Decimal] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class FertilizerStatsResponse(BaseModel):
    """Schema for fertilizer statistics"""
    total_applications: int = Field(..., description="Total number of applications")
    total_fertilizer_kg: Decimal = Field(..., description="Total fertilizer used in kg")
    total_cost: Decimal = Field(..., description="Total cost in ₹")
    total_nitrogen_kg: Decimal = Field(..., description="Total nitrogen applied in kg")
    total_phosphorus_kg: Decimal = Field(..., description="Total phosphorus applied in kg")
    total_potassium_kg: Decimal = Field(..., description="Total potassium applied in kg")
    avg_per_application_kg: Decimal = Field(..., description="Average per application")
    most_used_fertilizer: Optional[str] = Field(None, description="Most frequently used fertilizer")