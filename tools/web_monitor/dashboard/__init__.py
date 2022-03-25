from fastapi import Request, APIRouter
from fastapi.responses import RedirectResponse

from tools.web_monitor.template import templates
from tools.web_monitor.func import get_current_miner_list

from .ws import router as ws_router

router = APIRouter()
router.include_router(ws_router)


@router.get("/")
def index(request: Request):
    return RedirectResponse(request.url_for("dashboard"))


@router.get("/dashboard")
def dashboard(request: Request):
    return templates.TemplateResponse("index.html", {
        "request": request,
        "cur_miners": get_current_miner_list()
    })
