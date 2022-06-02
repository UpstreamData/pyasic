import base64
from io import BytesIO

import PySimpleGUI as sg
from PIL import Image

PAUSE_BTN = b"iVBORw0KGgoAAAANSUhEUgAAADIAAAAyCAYAAAAeP4ixAAABhmlDQ1BJQ0MgcHJvZmlsZQAAKJF9kT1Iw1AUhU9TtSIVByuIOGSogmBBtIijVLEIFkpboVUHk5f+CE0akhQXR8G14ODPYtXBxVlXB1dBEPwBcXRyUnSREu9LCi1ivPB4H+fdc3jvPkCol5lqdkwAqmYZqXhMzOZWxMAruuDDAKIYk5ipJ9ILGXjW1z31Ut1FeJZ335/Vq+RNBvhE4lmmGxbxOvH0pqVz3icOsZKkEJ8Tjxt0QeJHrssuv3EuOizwzJCRSc0Rh4jFYhvLbcxKhkocJQ4rqkb5QtZlhfMWZ7VcZc178hcG89pymuu0hhHHIhJIQoSMKjZQhoUI7RopJlJ0HvPwDzn+JLlkcm2AkWMeFaiQHD/4H/yerVmYmnSTgjGg88W2P0aAwC7QqNn297FtN04A/zNwpbX8lTow80l6raWFj4C+beDiuqXJe8DlDjD4pEuG5Eh+WkKhALyf0TflgP5boGfVnVvzHKcPQIZmtXQDHBwCo0XKXvN4d3f73P7tac7vB71FcsVdKt+2AAAABmJLR0QA/wD/AP+gvaeTAAAACXBIWXMAAA3XAAAN1wFCKJt4AAAAB3RJTUUH5gYBFTUTB1ciCQAAArVJREFUaN7dmktrU0EUx38Zal20leITF2mrBbuyirFiBQt1E7+AFvWbqO13EAqFgqB1IT52LoxQddcHtctKU62P2oUL+wBdpqmLnAvjNcnNnbn35k7+cCBkhpn53XmdMzMZolMvMApcBAaAPuAI0Cnpf4At4CuwBiwB74ENUqBTwARQBPYNbRUYF/DENQjMACULAL/tAa+AoSQATghAOUKAavZc6opFt4CdmAF02wbGogRoB6YTBPDblLTBSh1AoYkQnr0FDplCdAELKYDwbF5bykMNp0KKIPSeORgGZDqFEPqcaUg3Uwzh2Z1G9okdB0B2gZP1QJ44AOHZo1oQFxLYsaO0MnCuGshLhyA8e+Y1PqN5sZ8BZbjn7AOLwDcgCwzXKasMzAGbUu8lrR1hVQZOA9+9PyYsvspPIO+rYETiDH/eDeCqL29eyjCt/55eWNFinOZrfK1hn5tfkv+qKW8xPz/qkZ3p11gI6Po3Wt5CQN5Fi3ZkFXDNwqn8FJC+Zpg3rEYVkLMooBQivWRZVj3llBwUuK4BJcuX6+pXQHcLgHQrk2AlhepStIiUnAC6rt9KfHvXtauALy0Asq7Ez3JdRQV8sCigLUR6m2VZ9bSs5GjfVGeCdlzDvGH1zvuxGoMbfyWEG3/dwo1f0QsaTzCwGqkCYRNY3dVD3T5g3TLUXZIVsAe4HBDqzgM/xM8bsgh194B+PdQFeOHg4cPTanTnHTwOGqzVVY8dAnlYb8wdp3JTlHaIbeBY0AS64QDI7UZXg6kUQ0yGWdYOAK9TCDGLwX1ip6z3aYGYs4lmO1LSM7NU7jSt1N7kOTMpQz0yjSW8NG/JChqLDgMPxMeJc8eekT0tdp0lvkc1OZqgXuC+HO2bAqxQuePosWlIJkKoLP8/PDvKvw/PflF5eFYEliWy24yi8r9Buqx661BEjQAAAABJRU5ErkJggg=="
RECORD_BTN = b"iVBORw0KGgoAAAANSUhEUgAAADIAAAAyCAYAAAAeP4ixAAABhWlDQ1BJQ0MgcHJvZmlsZQAAKJF9kT1Iw1AUhU9Ta0UqDlYQcchQnSwUFXGUKhbBQmkrtOpg8tIfoUlDkuLiKLgWHPxZrDq4OOvq4CoIgj8gjk5Oii5S4n1JoUWMFx7v47x7Du/dBwiNClPNrhigapaRTsTFXH5FDL6iGz4MIoaAxEw9mVnIwrO+7qmX6i7Ks7z7/qw+pWAywCcSzzLdsIjXiac3LZ3zPnGYlSWF+Jx43KALEj9yXXb5jXPJYYFnho1seo44TCyWOljuYFY2VOIp4oiiapQv5FxWOG9xVis11ronf2GooC1nuE5rBAksIokURMioYQMVWIjSrpFiIk3ncQ//sONPkUsm1wYYOeZRhQrJ8YP/we/ZmsXJCTcpFAcCL7b9MQoEd4Fm3ba/j227eQL4n4Erre2vNoCZT9LrbS1yBPRvAxfXbU3eAy53gKEnXTIkR/LTEopF4P2MvikPDNwCvavu3FrnOH0AsjSrpRvg4BAYK1H2mse7ezrn9m9Pa34/WbVynangsIwAAAAGYktHRAD/AP8A/6C9p5MAAAAJcEhZcwAADdcAAA3XAUIom3gAAAAHdElNRQfmBgEVMgjCc30iAAAC7klEQVRo3t2az2sTQRTHPztiFdqqNP5A0CZWUClYxejFg1CPnrVF/Qu8+A/4438QC4WCoBVBojcP9lDrQVBBe6wasdhIj01biUeb9bBv7DYmaXdmdrPrF96hKftmPjPz5r2dWQ93ygPDwFngOFAAckCP/P8XUAW+A1+BD8Br4Acp0BHgLlAGfEP7AtwR8MQ1BEwCvy0AGm0NeAGcSwLggADUHQI0s5K0FYuuAisxA4RtGRh1CdAFTCQI0Gjj0gcrdQNTHYTQ9grYZQrRC7xPAYS2d6GtPNJymkoRRHhmdkQBmUghRDhmtqSRFENou76VPLGSAZBV4GA7kMcZgND2sBXEmQQytkurA6d057eFQO4Dgy4z6QhwQYqnAWDObaXhAX3Ac/2HrmK/AcrW+w1JQIDvrfsPfghG0qtF2Xraqy5jVNEzchO4aDv6l4CdMjqNEDJqnieJ4DxwyH6WPGAJeKMbKwPHbCAKTWZgM/ngL4BXsoP5DAx68ma3kDSEY5h+Zbuk8i2WUYS14eXtY2VYAUWbwFYOIlaJLwsVlRwUGJfHrmTp64SS7ctUvkMWG18DCthtGuQ2sdEsVkbMH9+jTGc1F8OhgIXPXsV/IgXUTB6sxtAZC581Bfw0ebK0Xju5inTfIimuKmDestZxWc2aal7JgbLZfDqksPRVVsBH06fHpY52UYtblvWziuBo31gVy1jxwa/Yj8WMkr6UTT2UgtLZM4FxVPl+AhZ1Hnli40nD1CMuJwcQf/uud4qC7F5Ze9VdA44ClXBDz4DLrg8fcqFkV8K5nhJcd2zQ6QweBw21InyUIZAH7aZqP8FNUdohloF9m627KxkAuRYlaacVYizKbrAdeJlCiGkM7hN7CK670gLxFoOrN63ulMzMtItDm64Ox8yYLHVnGk14a67KDhqL+oB7UuPEmbEnJafFrpPE91FNkQ4oD9yWdwJTgDngFtDfqRf+Rh3m3w/P9rLxw7Mlgg/PysAsMAMsumj8D9eE1oYpe82nAAAAAElFTkSuQmCC"
RESUME_BTN = b"iVBORw0KGgoAAAANSUhEUgAAADIAAAAyCAYAAAAeP4ixAAABhmlDQ1BJQ0MgcHJvZmlsZQAAKJF9kT1Iw1AUhU9TtSIVByuIOGSogmBBtIijVLEIFkpboVUHk5f+CE0akhQXR8G14ODPYtXBxVlXB1dBEPwBcXRyUnSREu9LCi1ivPB4H+fdc3jvPkCol5lqdkwAqmYZqXhMzOZWxMAruuDDAKIYk5ipJ9ILGXjW1z31Ut1FeJZ335/Vq+RNBvhE4lmmGxbxOvH0pqVz3icOsZKkEJ8Tjxt0QeJHrssuv3EuOizwzJCRSc0Rh4jFYhvLbcxKhkocJQ4rqkb5QtZlhfMWZ7VcZc178hcG89pymuu0hhHHIhJIQoSMKjZQhoUI7RopJlJ0HvPwDzn+JLlkcm2AkWMeFaiQHD/4H/yerVmYmnSTgjGg88W2P0aAwC7QqNn297FtN04A/zNwpbX8lTow80l6raWFj4C+beDiuqXJe8DlDjD4pEuG5Eh+WkKhALyf0TflgP5boGfVnVvzHKcPQIZmtXQDHBwCo0XKXvN4d3f73P7tac7vB71FcsVdKt+2AAAABmJLR0QA/wD/AP+gvaeTAAAACXBIWXMAAA3XAAAN1wFCKJt4AAAAB3RJTUUH5gYBFTUqWFKqAQAAApRJREFUaN7dms9LVFEUxz8+tBZp9NMISq0Wuskia9Gumr+ghUkF9X9k+gfUKihGhKCMiH4sgiglSltVULYrfEFF0aocNQwqcKYWnRev8c0w8+bc++71C2clnOOHN/fc+z33NqGnTuAwsB/oBrqAjUCr/P07UAA+AG+BF8AU8AkHtAMYBkLgd8qYAYYE3Lp6gTFgqQGA8igC94ADNgC2CEBJESApbkktIzoOzBsGiMccMKAJsAoYtQhQHnn5HxrSGmAiQ4goHgNr00K0Ac8dgIjiWayV1/VzmnAIIv5lVtcDMuogRHzN1KRjDkNEcbKWfWLeA5AFYGs1kGseQERxpRLEPgs7tmaUgD1JIHc8gojiZtIptqiQ+CNwH/hhCaQo9uGfhhWSFoD1kq8HmLYEMxgHCRUSPknYVM8pfelq8SYq2KGUcKpCEzkCfDYM0xEAOcMeZlK6y12DNQ4FQJ8FQ1YAjgKnxbtrqy+QQYEtjclw4pVy3u4A2GnZ74fAQeC8bGoa2gUwa3ixV1MO+KJQ+yvArwxBAPoVav8MWCEKgMUM6+eASwp5FgPgWwYA0a7/ENiskG+hGXhvuXP1ANfFNmjpXSDt0JZOAS+VIQDCZjmlmtY6YER7chjT9Eo5NG6Lis14fIx/HS865LGxOhMH6VK0ug8sWt2lcqsLcNvD4cONpEW518NxUG+lNnbVI5DL1fpxu9wUuQ4xV8vRpt8DkBO17pR5hyEu1rPltwDjDkI8SnOf2CrXXa5APE1z9Ra/DB135Eu0aZigfMZrokXzqDxguTUXpIMa0QbgguETbUkGee02nN5uzD2qsTHCXaZO4KyM9hvxE4Ni8FKrSRFqO8sfnm3i/4dns/x9eBaKX5kU99iw/gAVDZKvjiX0kgAAAABJRU5ErkJggg=="
STOP_BTN = b"iVBORw0KGgoAAAANSUhEUgAAADIAAAAyCAYAAAAeP4ixAAABhmlDQ1BJQ0MgcHJvZmlsZQAAKJF9kT1Iw1AUhU9TtSIVByuIOGSogmBBtIijVLEIFkpboVUHk5f+CE0akhQXR8G14ODPYtXBxVlXB1dBEPwBcXRyUnSREu9LCi1ivPB4H+fdc3jvPkCol5lqdkwAqmYZqXhMzOZWxMAruuDDAKIYk5ipJ9ILGXjW1z31Ut1FeJZ335/Vq+RNBvhE4lmmGxbxOvH0pqVz3icOsZKkEJ8Tjxt0QeJHrssuv3EuOizwzJCRSc0Rh4jFYhvLbcxKhkocJQ4rqkb5QtZlhfMWZ7VcZc178hcG89pymuu0hhHHIhJIQoSMKjZQhoUI7RopJlJ0HvPwDzn+JLlkcm2AkWMeFaiQHD/4H/yerVmYmnSTgjGg88W2P0aAwC7QqNn297FtN04A/zNwpbX8lTow80l6raWFj4C+beDiuqXJe8DlDjD4pEuG5Eh+WkKhALyf0TflgP5boGfVnVvzHKcPQIZmtXQDHBwCo0XKXvN4d3f73P7tac7vB71FcsVdKt+2AAAABmJLR0QA/wD/AP+gvaeTAAAACXBIWXMAAA3XAAAN1wFCKJt4AAAAB3RJTUUH5gYBFTYF2K7EmwAAAohJREFUaN7dmk1r00EQh58sWsG2NviKaG21oCer2HpUqN9Bi/pNrO13EIoNBcHWg/hy82APVQ+KCtKj0ohVFEUUm0ZabzZ6yPxhjUmb7Ow/2c0P5pKQ2X2yu7M7s5vBn/qAEWAYOAb0A7uALvl+DVgGPgBvgVfAE+ATAegwMAHkgT+OtgiMC3jTNQjMAr8VAJW2DjwATjcDYJ8AlDwCVLO70lYqugispAxgWwEY9QnQAUw3EaDSpqQPKnUCcy2ESOwRsMMVoht4GQBEYi+sUN7QdJoLCMIemW2NgEwHCGGvmbp0IWCIxC7Xs0+sRABSBPZvBHIrAojEbtaCONWEHdunlYAT1UDuRwSR2J2k8xnrFPsOMIrNcw14CnyVw+RG2iJz/Kxsuq4qAUeAj8kHE8p/5jrQ49CRHiCnbHvMdphXQmilgXljZ3auTlYdR6JSWZmarv3oNcA5RQeeAT89gBTFl6tGDDCkcPDdY7rwTfHbYSOFAk3U8CWNr6NGwlfsGjCy0GJX1rgkKwGq29AmMhK/Y9eqkRgeu4oGeN8GIEtGaq+aqelzmrsqb4AFhYO9nsuxrlpol0PjwcTRosJJzgOIpvz02nY0rkxuco4nhKyHGtoVO9XtB5aUC+6XHMW/1JnqHgDOANsVba4DA3aqC3AvwuLD7Wp0JyMsBw3WGqqZiEBubLYvFCKAKAB7NltA5yMAuVRvNJgKGGKykbC2FXgYIMQ8DveJXZSvu0KBeK7JZjsDGZl5yneaKnW0eM1MylT3ptEmh+ZliaCpaCdwTc44ae7Ys55znZo6TnqPaoZogfqAq1La1+QTY8AhTUcyHqF6+f/h2W7+fXj2g/LDs7ykp4+Bzz4a/wvuXq9nlKOgSQAAAABJRU5ErkJggg=="


def record_layout():
    buffer = BytesIO(base64.b64decode(sg.EMOJI_BASE64_HAPPY_BIG_SMILE))
    im1 = Image.open(buffer)
    with BytesIO() as output:
        im1.save(output, format="PNG")
        blank = output.getvalue()

    im2 = Image.new("RGBA", (50, 50), "#ffffff00")
    with BytesIO() as output:
        im2.save(output, format="PNG")
        blank = output.getvalue()

    record_layout = [
        [sg.Text("", key="record_status")],
        [
            sg.Text("Data Output File:"),
            sg.Input(key="record_file"),
            sg.SaveAs(
                "Select File",
                key="pick_record_file",
                file_types=(("PDF Files", "*.pdf"),),
                target="record_file",
            ),
        ],
        [
            sg.Push(),
            sg.pin(
                sg.Button(
                    image_data=RECORD_BTN,
                    button_color=(
                        sg.theme_background_color(),
                        sg.theme_background_color(),
                    ),
                    tooltip="Start Recording",
                    border_width=0,
                    key="start_recording",
                )
            ),
            sg.pin(
                sg.Button(
                    image_data=blank,
                    button_color=(
                        sg.theme_background_color(),
                        sg.theme_background_color(),
                    ),
                    border_width=0,
                    key="_placeholder",
                )
            ),
            sg.pin(
                sg.Button(
                    image_data=STOP_BTN,
                    tooltip="Stop Recording",
                    button_color=(
                        sg.theme_background_color(),
                        sg.theme_background_color(),
                    ),
                    border_width=0,
                    visible=False,
                    key="stop_recording",
                )
            ),
            sg.pin(
                sg.Button(
                    image_data=PAUSE_BTN,
                    tooltip="Pause Recording",
                    button_color=(
                        sg.theme_background_color(),
                        sg.theme_background_color(),
                    ),
                    border_width=0,
                    visible=False,
                    key="pause_recording",
                )
            ),
            sg.pin(
                sg.Button(
                    image_data=RESUME_BTN,
                    tooltip="Resume Recording",
                    button_color=(
                        sg.theme_background_color(),
                        sg.theme_background_color(),
                    ),
                    border_width=0,
                    visible=False,
                    key="resume_recording",
                )
            ),
            sg.Push(),
        ],
    ]
    return record_layout


record_window = sg.Window("Record Miner Data", record_layout(), modal=True)
