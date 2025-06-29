from fastapi import APIRouter
from .bmi import router as bmi_router
from .quote import router as quote_router
from .retrieval import router as retrieval_router
 
router = APIRouter()
router.include_router(bmi_router)
router.include_router(quote_router)
router.include_router(retrieval_router) 