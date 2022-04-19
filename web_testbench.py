from tools.web_testbench.app import app
import uvicorn
from logger import logger

def main():
    uvicorn.run("web_testbench:app", host="0.0.0.0", port=80)


if __name__ == "__main__":
    main()