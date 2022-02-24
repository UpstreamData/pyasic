from tools.web_monitor.app import app

if __name__ == '__main__':
    # app.run for running the sanic app inside the file
    app.run(host="0.0.0.0", port=80)
