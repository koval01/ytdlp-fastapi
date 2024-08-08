from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.staticfiles import StaticFiles

from app.middleware.process_time import ProcessTimeMiddleware
from app.middleware.referer import RefererCheckMiddleware
from app.middleware.node import NodeMiddleware
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
    CORSMiddleware,  # type: ignore[no-untyped-call]
    allow_origins=allowed_hosts,
    allow_credentials=True,
    allow_methods=["GET"],
    allow_headers=["X-Secret"],
)
app.add_middleware(
    TrustedHostMiddleware,  # type: ignore[no-untyped-call]
    allowed_hosts=allowed_hosts
)

app.add_middleware(NodeMiddleware)  # type: ignore[no-untyped-call]
app.add_middleware(ProcessTimeMiddleware)  # type: ignore[no-untyped-call]
app.add_middleware(RefererCheckMiddleware)  # type: ignore[no-untyped-call]

app.include_router(router)
