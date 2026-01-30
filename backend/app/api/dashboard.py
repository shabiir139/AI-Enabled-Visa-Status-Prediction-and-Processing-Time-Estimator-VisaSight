"""
Dashboard API Endpoints
"""

from fastapi import APIRouter
from typing import List, Optional

from app.models.schemas import (
    DashboardStats,
    ProcessingTimeDataPoint,
    ApprovalRateDataPoint,
    RuleVolatilityDataPoint,
)

router = APIRouter()


@router.get("/stats", response_model=DashboardStats)
async def get_dashboard_stats():
    """Get dashboard statistics."""
    return DashboardStats(
        total_cases=1247,
        pending_cases=423,
        approved_cases=789,
        average_processing_time=47,
        rule_updates_today=3,
    )


@router.get("/processing-time", response_model=List[ProcessingTimeDataPoint])
async def get_processing_time_chart(
    visa_type: Optional[str] = None,
    months: int = 6,
):
    """Get processing time trend data."""
    return [
        ProcessingTimeDataPoint(date="2025-08", average_days=52, median_days=48, upper_bound=75, lower_bound=28),
        ProcessingTimeDataPoint(date="2025-09", average_days=48, median_days=45, upper_bound=70, lower_bound=25),
        ProcessingTimeDataPoint(date="2025-10", average_days=55, median_days=51, upper_bound=80, lower_bound=30),
        ProcessingTimeDataPoint(date="2025-11", average_days=50, median_days=47, upper_bound=72, lower_bound=28),
        ProcessingTimeDataPoint(date="2025-12", average_days=58, median_days=54, upper_bound=85, lower_bound=32),
        ProcessingTimeDataPoint(date="2026-01", average_days=45, median_days=42, upper_bound=68, lower_bound=24),
    ]


@router.get("/approval-rates", response_model=List[ApprovalRateDataPoint])
async def get_approval_rate_chart(
    visa_type: Optional[str] = None,
    months: int = 6,
):
    """Get approval rate data by month."""
    return [
        ApprovalRateDataPoint(month="Aug", approved=72, denied=12, rfe=16),
        ApprovalRateDataPoint(month="Sep", approved=68, denied=14, rfe=18),
        ApprovalRateDataPoint(month="Oct", approved=75, denied=10, rfe=15),
        ApprovalRateDataPoint(month="Nov", approved=70, denied=13, rfe=17),
        ApprovalRateDataPoint(month="Dec", approved=65, denied=15, rfe=20),
        ApprovalRateDataPoint(month="Jan", approved=74, denied=11, rfe=15),
    ]


@router.get("/rule-volatility", response_model=List[RuleVolatilityDataPoint])
async def get_rule_volatility_chart(weeks: int = 12):
    """Get rule volatility index data."""
    return [
        RuleVolatilityDataPoint(week="W44", updates=5, impact_score=2.3),
        RuleVolatilityDataPoint(week="W45", updates=3, impact_score=1.5),
        RuleVolatilityDataPoint(week="W46", updates=8, impact_score=4.2),
        RuleVolatilityDataPoint(week="W47", updates=2, impact_score=0.8),
        RuleVolatilityDataPoint(week="W48", updates=6, impact_score=3.1),
        RuleVolatilityDataPoint(week="W49", updates=4, impact_score=2.0),
        RuleVolatilityDataPoint(week="W50", updates=7, impact_score=3.8),
        RuleVolatilityDataPoint(week="W51", updates=3, impact_score=1.2),
        RuleVolatilityDataPoint(week="W52", updates=9, impact_score=5.0),
        RuleVolatilityDataPoint(week="W01", updates=5, impact_score=2.5),
        RuleVolatilityDataPoint(week="W02", updates=4, impact_score=1.9),
        RuleVolatilityDataPoint(week="W03", updates=6, impact_score=3.2),
    ]
