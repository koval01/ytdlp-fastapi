from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

from app.middleware import process_time_middleware
from app.routes import router
from app.utils.config import settings

allowed_hosts = settings.ALLOWED_HOSTS.split(",")
app = FastAPI(
    title="YouTube Next Back-end",
    description="Proxy for the unofficial YouTube client",
    version="preview",
    docs_url="/",
    openapi_url=None if bool(settings.DISABLE_DOCS) else "/openapi.json"
)

app.mount("/static", StaticFiles(directory="static"), name="static")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_hosts,
    allow_credentials=True,
    allow_methods=["GET"],
    allow_headers=["X-Secret"],
)
app.add_middleware(
    TrustedHostMiddleware, allowed_hosts=allowed_hosts
)

app.include_router(router)

app.middleware("http")(process_time_middleware)
