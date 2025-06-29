from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.retrieval import AdvancedRetriever, RetrievalResult

router = APIRouter()

class RetrievalRequest(BaseModel):
    query: str
    k: int = 2

@router.post("/retrieval", response_model=RetrievalResult)
async def retrieval_endpoint(request: RetrievalRequest):
    retriever = AdvancedRetriever(k=request.k)
    try:
        result = retriever.retrieve(request.query)
        return result
    except Exception as e:
        # Log error and return HTTP 500
        import logging
        logging.getLogger("retrieval").error(f"Retrieval endpoint error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Retrieval error") 