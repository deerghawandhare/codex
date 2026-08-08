"""Pydantic models for the Vineeta API."""
from typing import Literal, Optional, List
from pydantic import BaseModel, Field

Language = Literal["hi", "mr", "en"]


class ChatRequest(BaseModel):
    user_id: str
    message: str
    language: Language = "hi"


class ChatResponse(BaseModel):
    reply: str
    language: Language


class ProfileRequest(BaseModel):
    user_id: str
    name: Optional[str] = None
    business_type: Optional[str] = None
    notes: Optional[str] = None


class ProfileResponse(BaseModel):
    status: str = "ok"


class NotificationItem(BaseModel):
    id: str
    title: str
    deadline: Optional[str] = None
    description: Optional[str] = None


class NotificationsResponse(BaseModel):
    notifications: List[NotificationItem]


class BudgetRequest(BaseModel):
    income: float = Field(gt=0, description="Monthly income in INR")
    expenses: float = Field(ge=0, description="Monthly expenses in INR")


class BudgetResponse(BaseModel):
    suggestion: str
    recommended_savings: float
