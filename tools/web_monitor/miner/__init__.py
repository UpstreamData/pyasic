from fastapi import Request, APIRouter

from tools.web_monitor.template import templates
from tools.web_monitor.func import get_current_miner_list

from .ws import router as ws_router

router = APIRouter()
router.include_router(ws_router)


@router.get("/")
def miner(_request: Request, _miner_ip):
    return get_miner


@router.get("/{miner_ip}")
def get_miner(request: Request, miner_ip):
    return templates.TemplateResponse(
        "miner.html",
        {"request": request, "cur_miners": get_current_miner_list(), "miner": miner_ip},
    )
