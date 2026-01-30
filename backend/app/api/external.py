from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from app.models.schemas import WaitTimeRecord, ExternalNorms
from app.services.data_fetcher import external_data_service

router = APIRouter(prefix="/external", tags=["External Data"])

@router.get("/processing-norms", response_model=ExternalNorms)
async def get_processing_norms(visa_type: str = Query(..., description="Visa type (e.g., H-1B, F-1)")):
    """
    Returns official processing time averages and ranges fetched from open-source datasets.
    Used as a benchmark for AI predictions.
    """
    try:
        return await external_data_service.fetch_processing_norms(visa_type)
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"External data source unavailable: {str(e)}")

@router.get("/visa-wait-times", response_model=List[WaitTimeRecord])
async def get_visa_wait_times(
    limit: int = 50, 
    visa_type: Optional[str] = None,
    consulate: Optional[str] = None
):
    """
    Returns current interview wait times for major consulates worldwide.
    """
    try:
        records = await external_data_service.fetch_wait_times()
        
        # Filtering
        if visa_type:
            records = [r for r in records if r.visa_type == visa_type]
        if consulate:
            records = [r for r in records if consulate.lower() in r.consulate.lower()]
            
        return records[:limit]
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Could not retrieve live wait times: {str(e)}")
