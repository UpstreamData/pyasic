from datetime import datetime, timedelta
from typing import List, Dict
from data import MinerData


import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator
from matplotlib.dates import DateFormatter
import numpy as np
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, inch
from reportlab.lib.styles import (
    ParagraphStyle,
    TA_CENTER,  # noqa - not declared in __all__
)
from reportlab.lib.utils import ImageReader
from reportlab.platypus import (
    SimpleDocTemplate,
    KeepInFrame,
    Table,
    Image,
    Paragraph,
    TableStyle,
    PageBreak,
    Spacer,
)
from io import BytesIO
from svglib.svglib import svg2rlg


async def generate_pdf(data: Dict[str, List[MinerData]], file_loc):
    doc = SimpleDocTemplate(
        file_loc,
        pagesize=letter,
        topMargin=0.25 * inch,
        leftMargin=1 * inch,
        rightMargin=1 * inch,
        bottomMargin=1 * inch,
        title=f"Recorded Data",
    )

    elements = []
    i = 0
    for item in data.keys():
        i += 1
        if not i == 1:
            elements.append(PageBreak())
        page_elem = await generate_page(data[item])
        for elem in page_elem:
            elements.append(elem)

    doc.build(
        elements,
    )


async def generate_page(data):
    title_style = ParagraphStyle(
        "Title",
        alignment=TA_CENTER,
        fontSize=25,
        spaceAfter=40,
        spaceBefore=150,
        fontName="Helvetica-Bold",
    )

    hr_graph = create_hr_graph(data)
    fan_graph = create_fans_graph(data)
    temp_graph = create_temp_graph(data)
    title = Paragraph(data[0].ip, style=title_style)

    elements = [
        title,
        await hr_graph,
        Spacer(0, 40),
        await temp_graph,
        Spacer(0, 40),
        await fan_graph,
    ]
    return elements


async def create_hr_graph(data):
    fig, ax = plt.subplots(figsize=(6, 2))
    xpoints = []
    ypoints = []
    for item in data:
        xpoints.append(item.datetime)
        ypoints.append(item.hashrate)
    for label in ax.get_xticklabels() + ax.get_yticklabels():
        label.set_fontsize(6)
    ax.plot(xpoints, ypoints)
    ylim = max(ypoints) * 1.4
    if ylim == 0:
        ylim = 10
    ax.set_ylim(0, ylim)
    date_form = DateFormatter("%H:%M:%S")
    ax.xaxis.set_major_formatter(date_form)
    ax.yaxis.set_major_formatter("{x:1.1f} TH/s")
    ax.set_title("Hashrate", fontsize=15)
    ax.yaxis.set_major_locator(MultipleLocator(5))
    ax.yaxis.set_minor_locator(MultipleLocator(1))

    imgdata = BytesIO()
    fig.savefig(imgdata, format="svg")
    imgdata.seek(0)  # rewind the data
    drawing = svg2rlg(imgdata)
    imgdata.close()
    plt.close("all")

    hr_graph = KeepInFrame(375, 375, [Image(drawing)], hAlign="CENTER")

    return hr_graph


async def create_fans_graph(data):
    fig, ax = plt.subplots(figsize=(6, 2))
    xpoints = []
    ypoints_f1 = []
    ypoints_f2 = []
    ypoints_f3 = []
    ypoints_f4 = []
    for item in data:
        xpoints.append(item.datetime)
        ypoints_f1.append(item.fan_1)
        ypoints_f2.append(item.fan_2)
        ypoints_f3.append(item.fan_3)
        ypoints_f4.append(item.fan_4)
    for label in ax.get_xticklabels() + ax.get_yticklabels():
        label.set_fontsize(6)
    for ypoints in [ypoints_f1, ypoints_f2, ypoints_f3, ypoints_f4]:
        if not ypoints == [-1 for x in range(len(ypoints))]:
            ax.plot(xpoints, ypoints)
    ax.set_ylim(0, 10000)
    date_form = DateFormatter("%H:%M:%S")
    ax.xaxis.set_major_formatter(date_form)
    ax.yaxis.set_major_formatter("{x:1.0f} RPM")
    ax.set_title("Fans", fontsize=15)

    imgdata = BytesIO()
    fig.savefig(imgdata, format="svg")
    imgdata.seek(0)  # rewind the data
    drawing = svg2rlg(imgdata)
    imgdata.close()
    plt.close("all")

    fans_graph = KeepInFrame(375, 375, [Image(drawing)], hAlign="CENTER")

    return fans_graph


async def create_temp_graph(data):
    fig, ax = plt.subplots(figsize=(6, 2))
    # plt.figure()
    xpoints = []
    ypoints = []
    for item in data:
        xpoints.append(item.datetime)
        ypoints.append(item.temperature_avg)
    for label in ax.get_xticklabels() + ax.get_yticklabels():
        label.set_fontsize(6)
    ax.plot(xpoints, ypoints)
    ax.set_ylim(0, 130)
    ax.yaxis.set_major_locator(MultipleLocator(20))
    ax.yaxis.set_minor_locator(MultipleLocator(5))
    date_form = DateFormatter("%H:%M:%S")
    ax.xaxis.set_major_formatter(date_form)
    ax.yaxis.set_major_formatter("{x:1.1f} C")
    ax.set_title("Temperature", fontsize=15)

    imgdata = BytesIO()
    fig.savefig(imgdata, format="svg")
    imgdata.seek(0)  # rewind the data
    drawing = svg2rlg(imgdata)
    imgdata.close()
    plt.close("all")

    temp_graph = KeepInFrame(375, 375, [Image(drawing)], hAlign="CENTER")

    return temp_graph
