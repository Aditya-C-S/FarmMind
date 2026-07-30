"""
Pydantic schemas for Activity Log model.
Handles request/response validation for activity endpoints.
"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import date, datetime
from uuid import UUID


class ActivityLogCreate(BaseModel):
    """Schema for creating a new activity log entry"""
    crop_id: UUID = Field(..., description="ID of the crop")
    activity_type: str = Field(..., min_length=1, max_length=50, description="Type of activity")
    activity_date: date = Field(..., description="Date when activity was performed")
    description: Optional[str] = Field(None, max_length=500, description="Activity description")
    performed_by: Optional[str] = Field(None, max_length=100, description="Person who performed activity")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional activity-specific data")


class ActivityLogUpdate(BaseModel):
    """Schema for updating an activity log entry"""
    activity_type: Optional[str] = Field(None, min_length=1, max_length=50)
    activity_date: Optional[date] = None
    description: Optional[str] = Field(None, max_length=500)
    performed_by: Optional[str] = Field(None, max_length=100)
    metadata: Optional[Dict[str, Any]] = None


class ActivityLogResponse(BaseModel):
    """Schema for activity log response"""
    activity_id: UUID
    crop_id: UUID
    activity_type: str
    activity_date: date
    description: Optional[str] = None
    performed_by: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class ActivityLogListResponse(BaseModel):
    """Schema for listing activities"""
    activity_id: UUID
    crop_id: UUID
    activity_type: str
    activity_date: date
    performed_by: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True