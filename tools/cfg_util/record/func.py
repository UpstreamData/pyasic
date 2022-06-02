from typing import List
from tools.cfg_util.record.manager import RecordingManager
import PySimpleGUI as sg


async def start_recording(
    ips: List[str], file: str, record_window: sg.Window, interval: int = 10
):
    record_window["start_recording"].update(visible=False)
    record_window["stop_recording"].update(visible=True)
    record_window["pause_recording"].update(visible=True)
    record_window["resume_recording"].update(visible=False)
    record_window["_placeholder"].update(visible=False)
    await RecordingManager().record(ips, file, record_window, interval=interval)


async def pause_recording(record_window):
    await RecordingManager().pause()
    record_window["resume_recording"].update(visible=True)
    record_window["start_recording"].update(visible=False)
    record_window["stop_recording"].update(visible=True)
    record_window["pause_recording"].update(visible=False)


async def stop_recording(record_window):
    await RecordingManager().stop()
    record_window["start_recording"].update(visible=True)
    record_window["stop_recording"].update(visible=False)
    record_window["pause_recording"].update(visible=False)
    record_window["resume_recording"].update(visible=False)
    record_window["_placeholder"].update(visible=True)


async def resume_recording(record_window):
    await RecordingManager().resume()
    record_window["start_recording"].update(visible=False)
    record_window["stop_recording"].update(visible=True)
    record_window["pause_recording"].update(visible=True)
    record_window["resume_recording"].update(visible=False)
