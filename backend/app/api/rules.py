"""
Visa Rules API Endpoints

Query visa rules with Supabase integration.
"""

from fastapi import APIRouter, HTTPException
from typing import List, Optional
from datetime import datetime, date

from app.models.schemas import (
    VisaRuleResponse,
    UpdateEventResponse,
    PaginatedResponse,
    VisaType,
    RuleCategory,
)
from app.db.supabase import supabase

router = APIRouter()


@router.get("", response_model=PaginatedResponse)
async def list_visa_rules(
    visa_type: Optional[str] = None,
    category: Optional[str] = None,
    page: int = 1,
    per_page: int = 10,
):
    """List visa rules with optional filtering."""
    try:
        query = supabase.table("visa_rules").select("*").eq("is_active", True)
        
        if visa_type:
            query = query.eq("visa_type", visa_type)
        if category:
            query = query.eq("rule_category", category)
        
        # Pagination
        start = (page - 1) * per_page
        query = query.range(start, start + per_page - 1)
        query = query.order("effective_date", desc=True)
        
        result = query.execute()
        
        rules = [
            VisaRuleResponse(
                id=row["id"],
                country=row.get("country", "USA"),
                visa_type=VisaType(row["visa_type"]),
                rule_category=RuleCategory(row["rule_category"]),
                title=row["title"],
                description=row["description"],
                effective_date=row["effective_date"],
                source_url=row.get("source_url"),
                created_at=row["created_at"],
            )
            for row in result.data
        ]
        
        # Get total count
        count_query = supabase.table("visa_rules").select("id", count="exact").eq("is_active", True)
        if visa_type:
            count_query = count_query.eq("visa_type", visa_type)
        if category:
            count_query = count_query.eq("rule_category", category)
        count_result = count_query.execute()
        total = count_result.count if hasattr(count_result, 'count') and count_result.count else len(result.data)
        
        return PaginatedResponse(
            items=rules,
            total=total,
            page=page,
            per_page=per_page,
            total_pages=(total + per_page - 1) // per_page if total > 0 else 1,
        )
    except Exception as e:
        print(f"Supabase error: {e}")
        # Return empty for demo
        return PaginatedResponse(
            items=[],
            total=0,
            page=page,
            per_page=per_page,
            total_pages=1,
        )


@router.get("/updates", response_model=List[UpdateEventResponse])
async def get_rule_updates(days_back: int = 7):
    """Get recent rule updates."""
    try:
        result = supabase.table("update_events")\
            .select("*")\
            .order("detected_at", desc=True)\
            .limit(20)\
            .execute()
        
        return [
            UpdateEventResponse(
                id=row["id"],
                rule_id=row["rule_id"],
                change_type=row["change_type"],
                previous_value=row.get("previous_value"),
                new_value=row.get("new_value"),
                detected_at=row["detected_at"],
                impact_score=row.get("impact_score", 0),
            )
            for row in result.data
        ]
    except Exception as e:
        print(f"Supabase error: {e}")
        return []


@router.get("/{rule_id}", response_model=VisaRuleResponse)
async def get_visa_rule(rule_id: str):
    """Get a specific rule by ID."""
    try:
        result = supabase.table("visa_rules").select("*").eq("id", rule_id).single().execute()
        
        if not result.data:
            raise HTTPException(status_code=404, detail="Rule not found")
        
        row = result.data
        return VisaRuleResponse(
            id=row["id"],
            country=row.get("country", "USA"),
            visa_type=VisaType(row["visa_type"]),
            rule_category=RuleCategory(row["rule_category"]),
            title=row["title"],
            description=row["description"],
            effective_date=row["effective_date"],
            source_url=row.get("source_url"),
            created_at=row["created_at"],
        )
    except HTTPException:
        raise
    except Exception as e:
        print(f"Supabase error: {e}")
        raise HTTPException(status_code=404, detail="Rule not found")
