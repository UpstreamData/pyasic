from fastapi import Request, APIRouter

from tools.web_monitor.template import templates
from tools.web_monitor.func import get_current_miner_list

from .ws import router as ws_router

import os

dir_path = "\\".join(os.path.dirname(os.path.realpath(__file__)).split("\\")[:-1])

router = APIRouter()
router.include_router(ws_router)


@router.get("/")
def scan(request: Request):
    return templates.TemplateResponse(
        "scan.html", {"request": request, "cur_miners": get_current_miner_list()}
    )


@router.post("/add_miners")
async def add_miners_scan(request: Request):
    miners = await request.json()
    with open(os.path.join(dir_path, "miner_list.txt"), "a+") as file:
        for miner_ip in miners["miners"]:
            file.write(miner_ip + "\n")
    return scan
