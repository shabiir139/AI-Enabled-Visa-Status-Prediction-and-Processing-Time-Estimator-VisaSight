"""
Visa Cases API Endpoints

CRUD operations for visa cases with Supabase integration.
"""

from fastapi import APIRouter, HTTPException, Header
from typing import List, Optional
from datetime import datetime
import uuid

from app.models.schemas import (
    VisaCaseCreate,
    VisaCaseResponse,
    CaseStatus,
    PaginatedResponse,
)
from app.db.supabase import supabase

router = APIRouter()


def get_user_id_from_token(authorization: Optional[str] = None) -> Optional[str]:
    """Extract user ID from JWT token."""
    if not authorization or not authorization.startswith("Bearer "):
        return None
    
    try:
        token = authorization.split(" ")[1]
        # Verify with Supabase
        user = supabase.auth.get_user(token)
        return user.user.id if user and user.user else None
    except Exception:
        return None


@router.post("", response_model=VisaCaseResponse)
async def create_visa_case(
    case_data: VisaCaseCreate,
    authorization: Optional[str] = Header(None)
):
    """Create a new visa case."""
    user_id = get_user_id_from_token(authorization)
    
    if not user_id:
        # Demo mode - create case without user
        user_id = "demo-user"
    
    try:
        data = {
            "user_id": user_id,
            "nationality": case_data.nationality,
            "visa_type": case_data.visa_type,
            "consulate": case_data.consulate,
            "submission_date": case_data.submission_date.isoformat(),
            "documents_submitted": case_data.documents_submitted,
            "sponsor_type": case_data.sponsor_type,
            "prior_travel": case_data.prior_travel,
            "current_status": "pending",
        }
        
        result = supabase.table("visa_cases").insert(data).execute()
        
        if result.data:
            row = result.data[0]
            return VisaCaseResponse(
                id=row["id"],
                user_id=row["user_id"],
                nationality=row["nationality"],
                visa_type=row["visa_type"],
                consulate=row["consulate"],
                submission_date=row["submission_date"],
                documents_submitted=row.get("documents_submitted", []),
                sponsor_type=row["sponsor_type"],
                prior_travel=row.get("prior_travel", False),
                current_status=CaseStatus(row["current_status"]),
                created_at=row["created_at"],
                updated_at=row.get("updated_at"),
            )
        else:
            # Fallback to mock response
            return VisaCaseResponse(
                id=str(uuid.uuid4()),
                user_id=user_id,
                nationality=case_data.nationality,
                visa_type=case_data.visa_type,
                consulate=case_data.consulate,
                submission_date=case_data.submission_date,
                documents_submitted=case_data.documents_submitted,
                sponsor_type=case_data.sponsor_type,
                prior_travel=case_data.prior_travel,
                current_status=CaseStatus.PENDING,
                created_at=datetime.utcnow(),
            )
    except Exception as e:
        print(f"Supabase error: {e}")
        # Fallback to mock for demo
        return VisaCaseResponse(
            id=str(uuid.uuid4()),
            user_id=user_id,
            nationality=case_data.nationality,
            visa_type=case_data.visa_type,
            consulate=case_data.consulate,
            submission_date=case_data.submission_date,
            documents_submitted=case_data.documents_submitted,
            sponsor_type=case_data.sponsor_type,
            prior_travel=case_data.prior_travel,
            current_status=CaseStatus.PENDING,
            created_at=datetime.utcnow(),
        )


@router.get("", response_model=PaginatedResponse)
async def list_visa_cases(
    page: int = 1, 
    per_page: int = 10,
    authorization: Optional[str] = Header(None)
):
    """List all visa cases for the current user."""
    user_id = get_user_id_from_token(authorization)
    
    try:
        query = supabase.table("visa_cases").select("*")
        
        if user_id:
            query = query.eq("user_id", user_id)
        
        # Pagination
        start = (page - 1) * per_page
        query = query.range(start, start + per_page - 1)
        query = query.order("created_at", desc=True)
        
        result = query.execute()
        
        # Get total count
        count_result = supabase.table("visa_cases").select("id", count="exact")
        if user_id:
            count_result = count_result.eq("user_id", user_id)
        count_data = count_result.execute()
        total = count_data.count if hasattr(count_data, 'count') else len(result.data)
        
        cases = [
            VisaCaseResponse(
                id=row["id"],
                user_id=row["user_id"],
                nationality=row["nationality"],
                visa_type=row["visa_type"],
                consulate=row["consulate"],
                submission_date=row["submission_date"],
                documents_submitted=row.get("documents_submitted", []),
                sponsor_type=row["sponsor_type"],
                prior_travel=row.get("prior_travel", False),
                current_status=CaseStatus(row["current_status"]),
                created_at=row["created_at"],
                updated_at=row.get("updated_at"),
            )
            for row in result.data
        ]
        
        return PaginatedResponse(
            items=cases,
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


@router.get("/{case_id}", response_model=VisaCaseResponse)
async def get_visa_case(
    case_id: str,
    authorization: Optional[str] = Header(None)
):
    """Get a specific visa case by ID."""
    try:
        result = supabase.table("visa_cases").select("*").eq("id", case_id).single().execute()
        
        if not result.data:
            raise HTTPException(status_code=404, detail="Case not found")
        
        row = result.data
        return VisaCaseResponse(
            id=row["id"],
            user_id=row["user_id"],
            nationality=row["nationality"],
            visa_type=row["visa_type"],
            consulate=row["consulate"],
            submission_date=row["submission_date"],
            documents_submitted=row.get("documents_submitted", []),
            sponsor_type=row["sponsor_type"],
            prior_travel=row.get("prior_travel", False),
            current_status=CaseStatus(row["current_status"]),
            created_at=row["created_at"],
            updated_at=row.get("updated_at"),
        )
    except HTTPException:
        raise
    except Exception as e:
        print(f"Supabase error: {e}")
        raise HTTPException(status_code=404, detail="Case not found")


@router.patch("/{case_id}", response_model=VisaCaseResponse)
async def update_visa_case(
    case_id: str, 
    updates: dict,
    authorization: Optional[str] = Header(None)
):
    """Update a visa case."""
    try:
        # Filter allowed update fields
        allowed_fields = {
            "nationality", "visa_type", "consulate", 
            "documents_submitted", "sponsor_type", 
            "prior_travel", "current_status"
        }
        filtered_updates = {k: v for k, v in updates.items() if k in allowed_fields}
        
        result = supabase.table("visa_cases").update(filtered_updates).eq("id", case_id).execute()
        
        if not result.data:
            raise HTTPException(status_code=404, detail="Case not found")
        
        row = result.data[0]
        return VisaCaseResponse(
            id=row["id"],
            user_id=row["user_id"],
            nationality=row["nationality"],
            visa_type=row["visa_type"],
            consulate=row["consulate"],
            submission_date=row["submission_date"],
            documents_submitted=row.get("documents_submitted", []),
            sponsor_type=row["sponsor_type"],
            prior_travel=row.get("prior_travel", False),
            current_status=CaseStatus(row["current_status"]),
            created_at=row["created_at"],
            updated_at=row.get("updated_at"),
        )
    except HTTPException:
        raise
    except Exception as e:
        print(f"Supabase error: {e}")
        raise HTTPException(status_code=500, detail="Failed to update case")


@router.delete("/{case_id}")
async def delete_visa_case(
    case_id: str,
    authorization: Optional[str] = Header(None)
):
    """Delete a visa case."""
    try:
        result = supabase.table("visa_cases").delete().eq("id", case_id).execute()
        
        if not result.data:
            raise HTTPException(status_code=404, detail="Case not found")
        
        return {"message": "Case deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        print(f"Supabase error: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete case")
