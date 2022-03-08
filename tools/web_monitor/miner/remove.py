from fastapi import Request
from fastapi.responses import RedirectResponse

from tools.web_monitor.app import app
from tools.web_monitor.func import get_current_miner_list


@app.get("/{miner_ip}/remove")
def get_miner(request: Request, miner_ip):
    miners = get_current_miner_list()
    miners.remove(miner_ip)
    with open("miner_list.txt", "w") as file:
        for miner_ip in miners:
            file.write(miner_ip + "\n")

    return RedirectResponse(request.url_for('dashboard'))
