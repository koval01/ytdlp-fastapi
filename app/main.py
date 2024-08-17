from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.staticfiles import StaticFiles

from app.middleware.node import NodeMiddleware
from app.middleware.process_time import ProcessTimeMiddleware
from app.middleware.referer import RefererCheckMiddleware

from asgi_correlation_id import CorrelationIdMiddleware

from app.routes import router
from app.utils.config import settings

# Parse the allowed hosts from the settings
allowed_hosts = settings.ALLOWED_HOSTS.split(",")

# Initialize the FastAPI application
app = FastAPI(
    title="YouTube Next Back-end",
    description="Proxy for the unofficial YouTube client",
    version="beta",
    docs_url="/",
    # Disable OpenAPI schema if specified in settings
    openapi_url=None if bool(settings.DISABLE_DOCS) else "/openapi.json"
)

# Conditionally mount static files if demo mode is not disabled
if not bool(settings.DISABLE_DEMO):
    app.mount("/static", StaticFiles(directory="static"), name="static")

app.add_middleware(
    CorrelationIdMiddleware,  # type: ignore[no-untyped-call]
    header_name='X-FAN-Request-ID'  # FAN - FastAPI Node
)

# Add CORS middleware to handle cross-origin requests
app.add_middleware(
    CORSMiddleware,  # type: ignore[no-untyped-call]
    allow_origins=["*"],  # Allow requests from any origin
    allow_credentials=True,  # Allow credentials in requests
    allow_methods=["GET"],  # Allow only GET requests
    allow_headers=["X-Secret", "X-Sign", "X-Client-Host"],  # Allow specific headers
    expose_headers=['X-FAN-Request-ID']
)

# Add middleware to restrict requests to allowed hosts
app.add_middleware(
    TrustedHostMiddleware,  # type: ignore[no-untyped-call]
    allowed_hosts=allowed_hosts  # Restrict requests to these hosts
)

# Add custom middlewares
app.add_middleware(NodeMiddleware)  # type: ignore[no-untyped-call]
app.add_middleware(ProcessTimeMiddleware)  # type: ignore[no-untyped-call]
app.add_middleware(RefererCheckMiddleware)  # type: ignore[no-untyped-call]

# Include application routes
app.include_router(router)
