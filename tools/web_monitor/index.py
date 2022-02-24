from tools.web_monitor.app import sio


@sio.event
async def connect(sid, _environ) -> None:
    """Event for connection"""
    await sio.emit('init', "hello")
