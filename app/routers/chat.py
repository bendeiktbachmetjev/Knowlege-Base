from fastapi import APIRouter, Query, Body, HTTPException, Request, Depends, Security
from pydantic import BaseModel
from app.services.llm.agent import chat_with_agent
from slowapi import Limiter
from slowapi.util import get_remote_address
from app.limiter import limiter
from fastapi.security.api_key import APIKeyHeader
from app.services.llm.client import generate_response_with_memory

router = APIRouter()

class ChatRequest(BaseModel):
    user_message: str

class ChatResponse(BaseModel):
    response: str

API_KEY = "supersecretkey"  # Change this to your real key or load from env
api_key_header = APIKeyHeader(name="X-API-Key")

def check_api_key(api_key: str = Security(api_key_header)):
    if api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API Key")

@router.post("/chat", response_model=ChatResponse)
@limiter.limit("10/minute")  # Limit to 10 requests per minute per IP
async def chat_endpoint(request: Request, body: ChatRequest, api_key: str = Security(check_api_key)):
    try:
        answer = chat_with_agent(body.user_message)
        return ChatResponse(response=answer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Agent error: {str(e)}")

@router.post("/memory-chat", response_model=ChatResponse)
@limiter.limit("10/minute")  # Limit to 10 requests per minute per IP
async def memory_chat_endpoint(request: Request, body: ChatRequest, api_key: str = Security(check_api_key)):
    """Chat endpoint with classic conversational memory (no tools, just LLM+memory)."""
    answer = generate_response_with_memory(body.user_message)
    return ChatResponse(response=answer)

@router.get("/test-gpt")
def test_gpt(prompt: str = Query(..., description="Prompt for GPT-4")):
    """
    Temporary endpoint to test GPT-4 integration via llm_client.
    Returns the model's response to the given prompt.
    """
    return {"reply": generate_response(prompt)}
