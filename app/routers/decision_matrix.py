from fastapi import APIRouter, HTTPException, Security, Request
from pydantic import BaseModel, Field
from typing import List
from app.services.core.decision_matrix import calculate_decision_matrix
from fastapi.security.api_key import APIKeyHeader
from app.limiter import limiter

router = APIRouter()

API_KEY = "supersecretkey"  # Change this to your real key or load from env
api_key_header = APIKeyHeader(name="X-API-Key")

def check_api_key(api_key: str = Security(api_key_header)):
    if api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API Key")

class DecisionMatrixRequest(BaseModel):
    options: List[str] = Field(..., description="List of options to choose from.")
    criteria: List[str] = Field(..., description="List of criteria for evaluation.")
    weights: List[float] = Field(..., description="List of weights for each criterion.")
    scores: List[List[float]] = Field(..., description="Matrix of scores: each row is an option, each column is a criterion.")

class DecisionMatrixResponse(BaseModel):
    result: dict

@router.post("/decision-matrix", response_model=DecisionMatrixResponse)
@limiter.limit("10/minute")
def decision_matrix_endpoint(
    request: Request,
    body: DecisionMatrixRequest,
    api_key: str = Security(check_api_key)
):
    """Endpoint to calculate weighted decision matrix."""
    try:
        result = calculate_decision_matrix(
            options=body.options,
            criteria=body.criteria,
            weights=body.weights,
            scores=body.scores
        )
        return DecisionMatrixResponse(result=result)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) 