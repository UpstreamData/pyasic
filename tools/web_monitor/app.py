import os

import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles

from tools.web_monitor.dashboard import router as dashboard_router
from tools.web_monitor.miner import router as miner_router
from tools.web_monitor.scan import router as scan_router
from tools.web_monitor._settings import router as settings_router

app = FastAPI()

app.mount(
    "/static",
    StaticFiles(directory=os.path.join(os.path.dirname(__file__), "static")),
    name="static",
)

app.include_router(dashboard_router, tags=["dashboard"])
app.include_router(miner_router, tags=["miner"], prefix="/miner")
app.include_router(scan_router, tags=["scan"], prefix="/scan")
app.include_router(settings_router, tags=["settings"], prefix="/settings")


@app.get("/remove_all_miners")
async def remove_all_miners(request: Request):
    file = open("miner_list.txt", "w")
    file.close()
    return RedirectResponse(request.url_for("settings"))


if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=80)
