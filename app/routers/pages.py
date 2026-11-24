import os

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.get("/map", response_class=HTMLResponse, include_in_schema=False)
def show_map(request: Request):
    return templates.TemplateResponse(
        request,
        "map.html",
        {"maps_key": os.getenv("GOOGLE_MAPS_JS_API_KEY", "")},
    )
