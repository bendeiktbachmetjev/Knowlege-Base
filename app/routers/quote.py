from fastapi import APIRouter, Request, Depends, Security, HTTPException
from fastapi.security.api_key import APIKeyHeader
from app.services.core.quote import get_quote
from slowapi import Limiter
from slowapi.util import get_remote_address
from app.limiter import limiter

router = APIRouter()

API_KEY = "supersecretkey"  # Change this to your real key or load from env
api_key_header = APIKeyHeader(name="X-API-Key")

def check_api_key(api_key: str = Security(api_key_header)):
    if api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API Key")

@router.get("/quote")
@limiter.limit("10/minute")  # Limit to 10 requests per minute per IP
def get_random_quote(request: Request, api_key: str = Security(check_api_key)):
    """Endpoint to get a random motivational quote."""
    return {"quote": get_quote()}

# Quote endpoint will be implemented here
