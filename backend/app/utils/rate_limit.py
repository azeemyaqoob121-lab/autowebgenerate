"""Rate limiting configuration using SlowAPI"""
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi import Request, Response
from fastapi.responses import JSONResponse
import logging

from app.config import settings
from app.schemas.errors import ErrorCode, ErrorDetail, ErrorResponse

# Module logger
logger = logging.getLogger(__name__)


def get_redis_uri() -> str:
    """
    Build Redis URI from settings.

    Returns:
        str: Redis connection URI or empty string to use in-memory storage
    """
    if settings.REDIS_HOST and settings.REDIS_PORT:
        redis_uri = f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}"
        if hasattr(settings, 'REDIS_DB'):
            redis_uri += f"/{settings.REDIS_DB}"
        return redis_uri
    return ""


def get_rate_limiter_key(request: Request) -> str:
    """
    Custom key function for rate limiting.

    Uses a combination of:
    - Remote IP address
    - User ID if authenticated
    - API key if present

    Args:
        request: FastAPI request object

    Returns:
        str: Rate limiter key
    """
    # Start with IP address
    key = get_remote_address(request)

    # Add user ID if authenticated
    if hasattr(request.state, 'user') and request.state.user:
        user_id = getattr(request.state.user, 'id', None)
        if user_id:
            key = f"user:{user_id}"

    # Add API key if present (for future API key auth)
    api_key = request.headers.get('X-API-Key')
    if api_key:
        key = f"apikey:{api_key}"

    return key


# Initialize limiter with configuration
redis_uri = get_redis_uri()
storage_uri = redis_uri if redis_uri else "memory://"

limiter = Limiter(
    key_func=get_rate_limiter_key,
    storage_uri=storage_uri,
    default_limits=[],  # No default limits - set per route
    headers_enabled=True,  # Add X-RateLimit-* headers to responses
    swallow_errors=True,  # Don't crash if Redis is down, fall back to no limiting
)

# Log rate limiter configuration
logger.info(
    "Rate limiter initialized",
    extra={
        "storage": "redis" if redis_uri else "memory",
        "redis_uri": redis_uri if redis_uri else "in-memory",
    }
)


async def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded) -> JSONResponse:
    """
    Custom handler for rate limit exceeded errors.

    Formats rate limit errors in our standardized error response format.

    Args:
        request: FastAPI request object
        exc: RateLimitExceeded exception

    Returns:
        JSONResponse with ErrorResponse format
    """
    # Extract request_id if available
    request_id = getattr(request.state, 'request_id', 'unknown')

    # Extract retry-after from exception if available
    retry_after = None
    if hasattr(exc, 'detail'):
        # Parse retry-after from exception detail
        # SlowAPI format: "X per Y" where Y could be "minute", "hour", etc.
        try:
            # Attempt to extract seconds from exception
            retry_after = 60  # Default to 1 minute
        except:
            pass

    # Create error response
    error_details = {
        'request_id': request_id,
        'path': str(request.url.path),
        'limit': str(exc.detail) if hasattr(exc, 'detail') else "Rate limit exceeded",
    }

    if retry_after:
        error_details['retry_after_seconds'] = retry_after

    error_response = ErrorResponse(
        error=ErrorDetail(
            code=ErrorCode.RATE_LIMIT_EXCEEDED,
            message="Too many requests. Please slow down and try again later.",
            details=error_details
        )
    )

    # Log rate limit violation
    logger.warning(
        f"Rate limit exceeded: {request.method} {request.url.path}",
        extra={
            'request_id': request_id,
            'path': request.url.path,
            'client_ip': get_remote_address(request),
            'limit': str(exc.detail) if hasattr(exc, 'detail') else 'unknown',
        }
    )

    # Return 429 response with Retry-After header
    headers = {"Retry-After": str(retry_after)} if retry_after else {}

    return JSONResponse(
        status_code=429,
        content=error_response.model_dump(),
        headers=headers
    )


# Common rate limit strings
# Format: "X per Y" where X is number of requests and Y is time period
class RateLimits:
    """
    Predefined rate limit configurations.

    Usage:
        from app.utils.rate_limit import limiter, RateLimits

        @router.get("/endpoint")
        @limiter.limit(RateLimits.STANDARD)
        async def endpoint(request: Request):
            ...
    """

    # General API limits
    STANDARD = "100/minute;1000/hour"  # Standard rate for most endpoints
    STRICT = "10/minute;100/hour"      # Strict rate for sensitive operations
    RELAXED = "300/minute;3000/hour"   # Relaxed rate for read-only operations

    # Authentication endpoints
    AUTH_LOGIN = "5/minute;20/hour"    # Login attempts
    AUTH_REGISTER = "3/minute;10/hour" # Registration attempts
    AUTH_REFRESH = "10/minute;50/hour" # Token refresh

    # Resource creation
    CREATE_BUSINESS = "30/minute;200/hour"  # Business creation
    CREATE_EVALUATION = "50/minute;500/hour"  # Evaluation creation

    # Search and listing
    SEARCH = "60/minute;600/hour"      # Search operations
    LIST = "100/minute;1000/hour"      # List operations


def register_rate_limiter(app) -> None:
    """
    Register rate limiter with FastAPI application.

    This function should be called during application initialization.

    Args:
        app: FastAPI application instance

    Usage:
        from app.utils.rate_limit import register_rate_limiter
        app = FastAPI()
        register_rate_limiter(app)
    """
    # Add rate limiter to app state
    app.state.limiter = limiter

    # Register custom rate limit exceeded handler
    app.add_exception_handler(RateLimitExceeded, rate_limit_exceeded_handler)

    logger.info("Rate limiter registered with application")
