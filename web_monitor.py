from tools.web_monitor.app import app
import uvicorn


def main():
    uvicorn.run("web_monitor:app", host="0.0.0.0", port=80)


if __name__ == "__main__":
    main()
