from fastapi import Request, APIRouter
from fastapi.responses import RedirectResponse

from tools.web_monitor.template import templates
from tools.web_monitor.func import get_current_miner_list
from tools.web_monitor.settings.func import get_current_settings, update_settings


router = APIRouter()


@router.route("/", methods=["GET", "POST"])
async def settings(request: Request):
    return templates.TemplateResponse("settings.html", {
        "request": request,
        "cur_miners": get_current_miner_list(),
        "settings": get_current_settings()
    })


@router.post("/update")
async def update_settings_page(request: Request):
    data = await request.form()
    graph_data_sleep_time = data.get('graph_data_sleep_time')
    miner_data_timeout = data.get('miner_data_timeout')
    miner_identify_timeout = data.get('miner_identify_timeout')
    new_settings = {
        "graph_data_sleep_time": int(graph_data_sleep_time),
        "miner_data_timeout": int(miner_data_timeout),
        "miner_identify_timeout": int(miner_identify_timeout),
    }
    update_settings(new_settings)
    return RedirectResponse(request.url_for("settings"))
