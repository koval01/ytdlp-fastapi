"""
Router for templates
"""

from fastapi import Request, APIRouter
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app.utils.config import settings

router = APIRouter()
templates = Jinja2Templates(directory="templates")


@router.get(
    "/demo/{video_id}",
    summary="Demo page",
    response_class=HTMLResponse,
    tags=["Templates"]
)
async def demo(request: Request, video_id: str) -> HTMLResponse:
    """Request handler"""
    return templates.TemplateResponse(
        request=request, name="demo.html", context={
            "video_id": video_id, "secret_key": settings.SECRET_KEY
        }
    )
