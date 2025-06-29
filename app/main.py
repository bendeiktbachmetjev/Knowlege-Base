from fastapi import FastAPI, Request
from slowapi.errors import RateLimitExceeded
from slowapi import _rate_limit_exceeded_handler
from app.limiter import limiter
from app.routers import chat, quote, decision_matrix
# from app.routers import bmi, quote, retrieval  # Remove from production
# from app.routers import health  # if health-check exists, connect it

app = FastAPI()

# Register limiter and exception handler
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Health check endpoint
@app.get("/health")
async def health_check(request: Request):
    """Health check endpoint for Render and monitoring."""
    return {"status": "ok"}

# Routers registration
app.include_router(chat.router)
app.include_router(quote.router)  # only for tests
app.include_router(decision_matrix.router)  # decision matrix endpoint
# app.include_router(health.router)  # if health-check exists
# app.include_router(bmi.router)  # only for tests
# app.include_router(retrieval.router)  # only for tests

