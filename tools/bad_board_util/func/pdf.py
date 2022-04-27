import datetime
from base64 import b64decode
from io import BytesIO

from reportlab.lib.pagesizes import letter, inch
from reportlab.lib.utils import ImageReader
from reportlab.lib.styles import ParagraphStyle, TA_CENTER
from reportlab.platypus import (
    SimpleDocTemplate,
    KeepInFrame,
    Table,
    Image,
    Paragraph,
    TableStyle,
    PageBreak,
)
from reportlab.lib import colors

import ipaddress


from miners.miner_factory import MinerFactory
from tools.bad_board_util.func.decorators import disable_buttons
from tools.bad_board_util.img import IMAGE_SELECTION_MATRIX, LOGO
from tools.bad_board_util.layout import window


def add_page_header(canvas, doc):
    canvas.saveState()
    canvas.drawCentredString(
        (letter[0] / 16) * 14,
        letter[1] - 57,
        datetime.datetime.now().strftime("%Y-%b-%d"),
    )
    img_dec = b64decode(LOGO)
    img = BytesIO(img_dec)
    img.seek(0)

    canvas.drawImage(
        ImageReader(img),
        30,
        letter[1] - 65,
        150,
        35,
    )
    canvas.drawString(letter[0] - 60, 20, "Page " + str(doc.page))
    canvas.restoreState()


@disable_buttons
async def save_report(file_location):
    data = {}
    for line in window["ip_table"].Values:
        data[line[0]] = {
            "Model": line[1],
            "Total Chips": line[2],
            "Left Chips": line[3],
            "Center Chips": line[5],
            "Right Chips": line[7],
            "Nominal": 1,
        }

    async for miner in MinerFactory().get_miner_generator([key for key in data.keys()]):
        if miner:
            data[str(miner.ip)]["Nominal"] = miner.nominal_chips

    list_data = []
    for ip in data.keys():
        new_data = data[ip]
        new_data["IP"] = ip
        list_data.append(new_data)

    list_data = sorted(
        list_data, reverse=False, key=lambda x: ipaddress.ip_address(x["IP"])
    )

    image_selection_data = {}
    for miner in list_data:
        miner_bad_boards = ""
        if miner["Left Chips"] < miner["Nominal"]:
            miner_bad_boards += "l"
        if miner["Center Chips"] < miner["Nominal"]:
            miner_bad_boards += "c"
        if miner["Right Chips"] < miner["Nominal"]:
            miner_bad_boards += "r"
        image_selection_data[miner["IP"]] = miner_bad_boards

    doc = SimpleDocTemplate(
        file_location,
        pagesize=letter,
        topMargin=1 * inch,
        leftMargin=1 * inch,
        rightMargin=1 * inch,
        bottomMargin=1 * inch,
        title=f"Board Report {datetime.datetime.now().strftime('%Y/%b/%d')}",
    )

    elements = []

    table_data = get_table_data(image_selection_data)

    miner_img_table = Table(
        table_data,
        colWidths=0.8 * inch,
        repeatRows=1,
        # rowHeights=[4 * inch],
    )

    miner_img_table.setStyle(
        TableStyle(
            [
                ("SPAN", (0, 0), (-1, 0)),
                ("LEFTPADDING", (0, 0), (-1, -1), 0),
                ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                ("BOTTOMPADDING", (0, 1), (-1, -1), 0),
                ("TOPPADDING", (0, 1), (-1, -1), 0),
                ("BOTTOMPADDING", (0, 0), (-1, 0), 20),
                ("TOPPADDING", (0, 0), (-1, 0), 20),
            ]
        )
    )

    elements.append(miner_img_table)
    elements.append(PageBreak())
    elements.append(create_data_table(list_data))
    elements.append(PageBreak())

    doc.build(
        elements,
        onFirstPage=add_page_header,
        onLaterPages=add_page_header,
    )


def create_data_table(data):
    left_bad_boards = 0
    right_bad_boards = 0
    center_bad_boards = 0
    table_data = []
    for miner in data:
        miner_bad_boards = 0
        if miner["Left Chips"] < miner["Nominal"]:
            miner_bad_boards += 1
            left_bad_boards += 1
        if miner["Center Chips"] < miner["Nominal"]:
            miner_bad_boards += 1
            right_bad_boards += 1
        if miner["Right Chips"] < miner["Nominal"]:
            miner_bad_boards += 1
            center_bad_boards += 1
        table_data.append(
            [
                miner["IP"],
                miner["Total Chips"],
                miner["Left Chips"],
                miner["Center Chips"],
                miner["Right Chips"],
                miner_bad_boards,
            ]
        )

    table_data.append(
        [
            "Total",
            sum([miner[1] for miner in table_data]),
            sum([miner[2] for miner in table_data]),
            sum([miner[3] for miner in table_data]),
            sum([miner[4] for miner in table_data]),
            sum([miner[5] for miner in table_data]),
        ]
    )

    table_data[:0] = (
        [
            "IP",
            "Total Chips",
            "Left Board Chips",
            "Center Board Chips",
            "Right Board Chips",
            "Failed Boards",
        ],
    )

    # create the table
    t = Table(table_data, repeatRows=1)

    # generate a basic table style
    table_style = TableStyle(
        [
            # line for below titles
            ("LINEBELOW", (0, 0), (-1, 0), 2, colors.black),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            # line for above totals
            ("LINEABOVE", (0, -1), (-1, -1), 2, colors.black),
            ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"),
            # line for beside unit #
            ("LINEAFTER", (0, 0), (0, -1), 2, colors.black),
            ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
            # gridlines and outline of table
            ("INNERGRID", (0, 0), (-1, -1), 0.25, colors.black),
            ("BOX", (0, 0), (-1, -1), 2, colors.black),
        ]
    )

    # set the styles to the table
    t.setStyle(table_style)

    # zebra stripes on table
    for each in range(len(table_data)):
        if each % 2 == 0:
            bg_color = colors.whitesmoke
        else:
            bg_color = colors.lightgrey

        t.setStyle(TableStyle([("BACKGROUND", (0, each), (-1, each), bg_color)]))

    return t


def get_table_data(data):
    IP_STYLE = ParagraphStyle(
        "IP Style",
        alignment=TA_CENTER,
        fontSize=7,
        fontName="Helvetica-Bold",
    )
    TITLE_STYLE = ParagraphStyle(
        "Title",
        alignment=TA_CENTER,
        fontSize=20,
        spaceAfter=10,
        fontName="Helvetica-Bold",
    )
    table_elems = [[Paragraph("Board Report", style=TITLE_STYLE)]]
    table_row = []
    table_style = TableStyle(
        [
            ("LEFTPADDING", (0, 0), (-1, -1), 0),
            ("RIGHTPADDING", (0, 0), (-1, -1), 0),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
            ("BOX", (0, 0), (-1, -1), 2, colors.black),
        ]
    )
    table_width = 0.8 * inch
    for ip in data.keys():
        img_dec = b64decode(IMAGE_SELECTION_MATRIX[data[ip]])
        img = BytesIO(img_dec)
        img.seek(0)
        image = KeepInFrame(table_width, table_width, [Image(img)])
        ip_para = Paragraph(ip, style=IP_STYLE)

        table_row.append(
            Table([[ip_para], [image]], colWidths=table_width, style=table_style)
        )

        # table_row.append(image)
        # table_row_txt.append(ip_para)

        if len(table_row) > 7:
            # table_elems.append(table_row_txt)
            # table_elems.append(table_row)
            table_elems.append(table_row)
            # table_row_txt = []
            table_row = []
    if not table_row == []:
        table_elems.append(table_row)
    return table_elems
