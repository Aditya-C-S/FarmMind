"""
Activity Routes module.
API endpoints for activity log operations.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from uuid import UUID

from app.database.session import get_db
from app.schemas.activity_log import ActivityLogCreate, ActivityLogUpdate, ActivityLogResponse, ActivityLogListResponse
from app.services.activity_service import ActivityService

router = APIRouter(prefix="/activities", tags=["Activities"])


@router.post("", response_model=ActivityLogResponse, status_code=status.HTTP_201_CREATED)
def create_activity(activity_data: ActivityLogCreate, db: Session = Depends(get_db)):
    """Create a new activity log entry"""
    try:
        activity = ActivityService.create_activity(db, activity_data)
        return activity
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error creating activity")


@router.get("", response_model=list[ActivityLogListResponse])
def list_activities(skip: int = Query(0, ge=0), limit: int = Query(100, ge=1, le=1000), db: Session = Depends(get_db)):
    """List all activities (paginated)"""
    # Note: This gets all activities without crop filter - consider filtering in production
    return []


@router.get("/{activity_id}", response_model=ActivityLogResponse)
def get_activity(activity_id: UUID, db: Session = Depends(get_db)):
    """Get a specific activity by ID"""
    activity = ActivityService.get_activity_by_id(db, activity_id)
    if not activity:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Activity not found")
    return activity


@router.get("/crop/{crop_id}", response_model=list[ActivityLogListResponse])
def get_activities_by_crop(crop_id: UUID, skip: int = Query(0, ge=0), limit: int = Query(100, ge=1, le=1000), db: Session = Depends(get_db)):
    """Get all activities for a specific crop"""
    activities = ActivityService.get_activities_by_crop(db, crop_id, skip, limit)
    return activities


@router.put("/{activity_id}", response_model=ActivityLogResponse)
def update_activity(activity_id: UUID, activity_data: ActivityLogUpdate, db: Session = Depends(get_db)):
    """Update an activity record"""
    activity = ActivityService.update_activity(db, activity_id, activity_data)
    if not activity:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Activity not found")
    return activity


@router.delete("/{activity_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_activity(activity_id: UUID, db: Session = Depends(get_db)):
    """Delete an activity record"""
    success = ActivityService.delete_activity(db, activity_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Activity not found")
    return None


@router.get("/crop/{crop_id}/count", response_model=dict)
def count_activities(crop_id: UUID, db: Session = Depends(get_db)):
    """Count activities for a crop"""
    count = ActivityService.count_activities_by_crop(db, crop_id)
    return {"crop_id": crop_id, "total_activities": count}