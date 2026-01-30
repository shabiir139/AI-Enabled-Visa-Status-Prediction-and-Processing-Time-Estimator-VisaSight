"""
Pydantic Models for VisaSight API
"""

from datetime import datetime, date
from typing import Optional, List, Dict, Any
from enum import Enum
from pydantic import BaseModel, Field
import uuid


class VisaType(str, Enum):
    F1 = "F-1"
    H1B = "H-1B"
    B1B2 = "B1/B2"
    L1 = "L-1"
    O1 = "O-1"
    J1 = "J-1"


class SponsorType(str, Enum):
    EMPLOYER = "employer"
    UNIVERSITY = "university"
    SELF = "self"
    FAMILY = "family"
    GOVERNMENT = "government"


class CaseStatus(str, Enum):
    PENDING = "pending"
    IN_REVIEW = "in_review"
    RFE_ISSUED = "rfe_issued"
    APPROVED = "approved"
    DENIED = "denied"
    WITHDRAWN = "withdrawn"


# Visa Case Models
class VisaCaseCreate(BaseModel):
    nationality: str
    visa_type: VisaType
    consulate: str
    submission_date: date
    documents_submitted: List[str] = []
    sponsor_type: SponsorType
    prior_travel: bool = False


class VisaCaseResponse(BaseModel):
    id: str
    user_id: Optional[str] = None
    nationality: str
    visa_type: VisaType
    consulate: str
    submission_date: date
    documents_submitted: List[str]
    sponsor_type: SponsorType
    prior_travel: bool
    current_status: CaseStatus
    created_at: datetime
    updated_at: Optional[datetime] = None


# Prediction Models
class StatusProbabilities(BaseModel):
    approved: float
    rfe: float
    denied: float


class ExplanationFactor(BaseModel):
    feature: str
    impact: str  # positive, negative, neutral
    contribution: float
    description: str


class PredictionExplanation(BaseModel):
    top_factors: List[ExplanationFactor]
    feature_importance: Dict[str, float]
    model_confidence: float


class PredictionResult(BaseModel):
    id: str
    visa_case_id: str
    predicted_status: StatusProbabilities
    estimated_days_remaining: int
    confidence_interval: tuple[int, int]
    model_version: str
    generated_at: datetime
    explanation: Optional[PredictionExplanation] = None


class PredictRequest(BaseModel):
    case_id: str
    case_data: Optional[Dict[str, Any]] = None


# Rule Models
class RuleCategory(str, Enum):
    ELIGIBILITY = "eligibility"
    DOCUMENTATION = "documentation"
    PROCESSING = "processing"
    FEES = "fees"
    INTERVIEW = "interview"
    TRAVEL_ADVISORY = "travel_advisory"


class VisaRuleResponse(BaseModel):
    id: str
    country: str
    visa_type: VisaType
    rule_category: RuleCategory
    title: str
    description: str
    effective_date: date
    source_url: Optional[str] = None
    created_at: datetime


class UpdateEventResponse(BaseModel):
    id: str
    rule_id: str
    change_type: str
    previous_value: Optional[str] = None
    new_value: Optional[str] = None
    detected_at: datetime
    impact_score: float


# Dashboard Models
class DashboardStats(BaseModel):
    total_cases: int
    pending_cases: int
    approved_cases: int
    average_processing_time: int
    rule_updates_today: int


class ProcessingTimeDataPoint(BaseModel):
    date: str
    average_days: int
    median_days: int
    upper_bound: int
    lower_bound: int


class ApprovalRateDataPoint(BaseModel):
    month: str
    approved: int
    denied: int
    rfe: int


class RuleVolatilityDataPoint(BaseModel):
    week: str
    updates: int
    impact_score: float



# External Data Models
class WaitTimeRecord(BaseModel):
    consulate: str
    visa_type: str
    wait_days: int
    last_updated: datetime
    source: str


class ExternalNorms(BaseModel):
    visa_type: str
    avg_processing_days: int
    min_days: int
    max_days: int
    confidence_score: float
    data_source: str


# Paginated Response
class PaginatedResponse(BaseModel):
    items: List
    total: int
    page: int
    per_page: int
    total_pages: int
