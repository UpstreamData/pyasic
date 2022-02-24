import socketio
from sanic import Sanic

app = Sanic("App")

# attach socketio
sio = socketio.AsyncServer(async_mode="sanic")
sio.attach(app)

app.static('/', "./public/index.html")
app.static('/index.css', "./static/index.css")
app.static('/index.js', "./static/index.js")

app.static('/scan', "./public/scan.html")
app.static('/settings', "./public/settings.html")
