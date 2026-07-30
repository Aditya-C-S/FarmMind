"""
Pydantic schemas for Disease History model.
Handles request/response validation for disease endpoints.
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import date, datetime
from uuid import UUID
from decimal import Decimal


class DiseaseHistoryCreate(BaseModel):
    """Schema for creating a new disease record"""
    crop_id: UUID = Field(..., description="ID of the crop")
    disease_name: str = Field(..., min_length=1, max_length=100, description="Name of disease")
    severity: str = Field(..., description="Severity level: low, medium, high")
    confidence: Decimal = Field(default=0, ge=0, le=100, description="Detection confidence (0-100)")
    detected_date: date = Field(..., description="Date when disease was detected")
    detected_by: str = Field(default="user_input", description="How disease was detected")
    treatment_applied: Optional[str] = Field(None, description="Treatment applied")
    treatment_date: Optional[date] = None
    status: Optional[str] = Field(default="active", description="Status: active, treated, resolved, worsened")
    prognosis: Optional[str] = Field(None, description="Expected progression")


class DiseaseHistoryUpdate(BaseModel):
    """Schema for updating a disease record"""
    severity: Optional[str] = None
    treatment_applied: Optional[str] = None
    treatment_date: Optional[date] = None
    status: Optional[str] = None
    prognosis: Optional[str] = None


class DiseaseHistoryResponse(BaseModel):
    """Schema for disease history response"""
    disease_id: UUID
    crop_id: UUID
    disease_name: str
    severity: str
    confidence: Decimal
    detected_date: date
    detected_by: str
    treatment_applied: Optional[str] = None
    treatment_date: Optional[date] = None
    status: str
    prognosis: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class DiseaseHistoryListResponse(BaseModel):
    """Schema for listing diseases"""
    disease_id: UUID
    crop_id: UUID
    disease_name: str
    severity: str
    status: str
    detected_date: date
    created_at: datetime
    
    class Config:
        from_attributes = True