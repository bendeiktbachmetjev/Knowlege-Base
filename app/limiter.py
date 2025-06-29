from slowapi import Limiter
from slowapi.util import get_remote_address

# Limiter instance for global rate limiting (10 requests per minute per IP)
limiter = Limiter(key_func=get_remote_address, default_limits=["10/minute"]) 