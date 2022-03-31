import os
from fastapi.templating import Jinja2Templates


templates = Jinja2Templates(
    directory=os.path.join(os.path.dirname(__file__), "templates")
)
