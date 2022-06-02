from typing import List
from tools.cfg_util.record.manager import RecordingManager
from tools.cfg_util.record.layout import record_window


async def start_recording(ips: List[str], file: str, interval: int = 10):
    record_window["start_recording"].update(visible=False)
    record_window["stop_recording"].update(visible=True)
    record_window["pause_recording"].update(visible=True)
    record_window["resume_recording"].update(visible=False)
    record_window["_placeholder"].update(visible=False)
    await RecordingManager().record(
        ips,
        file,
    )


async def pause_recording():
    await RecordingManager().pause()
    record_window["resume_recording"].update(visible=True)
    record_window["start_recording"].update(visible=False)
    record_window["stop_recording"].update(visible=True)
    record_window["pause_recording"].update(visible=False)


async def stop_recording():
    await RecordingManager().stop()
    record_window["start_recording"].update(visible=True)
    record_window["stop_recording"].update(visible=False)
    record_window["pause_recording"].update(visible=False)
    record_window["resume_recording"].update(visible=False)
    record_window["_placeholder"].update(visible=True)


async def resume_recording():
    await RecordingManager().resume()
    record_window["start_recording"].update(visible=False)
    record_window["stop_recording"].update(visible=True)
    record_window["pause_recording"].update(visible=True)
    record_window["resume_recording"].update(visible=False)
