from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime
from src.schemas import PaginatedRequestModel

class MoodAnalyticsQueryParams(BaseModel):
    time_dimension: str = Field(..., description="time dimension, week/month/year")
    reference_date: str = Field(..., description="reference date, format: YYYY-MM-DD")

class MoodDataPoint(BaseModel):
    mood_value: int = Field(..., description="mood value (-10 to 10)")
    post_count: int = Field(..., description="number of posts with this mood value")
    post_ids: List[int] = Field(..., description="list of post IDs corresponding to this mood value")

class TimelinePoint(BaseModel):
    time_index: int = Field(..., description="time point index")
    time_point: str = Field(..., description="date of the time point (YYYY-MM-DD)")
    average_mood: float = Field(..., description="average mood value of the time point")
    data_points: List[MoodDataPoint] = Field([], description="all mood data points of the time point")

class TimeRange(BaseModel):
    start_date: str = Field(..., description="start date of the time range")
    end_date: str = Field(..., description="end date of the time range")
    dimension: str = Field(..., description="time dimension (week/month/year)")

class MoodSummary(BaseModel):
    total_posts: int = Field(..., description="total number of posts")
    average_mood: float = Field(..., description="average mood value")

class MoodAnalyticsResponse(BaseModel):
    time_range: TimeRange = Field(..., description="time range information")
    timeline: List[TimelinePoint] = Field(..., description="timeline data")
    summary: MoodSummary = Field(..., description="mood summary")
    
    class Config:
        from_attributes = True

class PostByIdsQueryParams(PaginatedRequestModel):
    post_ids: List[int] = Field(..., description="list of post IDs to get")