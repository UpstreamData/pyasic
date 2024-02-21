import asyncio
import importlib
import os
import warnings

from pyasic.miners.factory import MINER_CLASSES, MinerTypes

warnings.filterwarnings("ignore")


def path(cls):
    module = importlib.import_module(cls.__module__)
    return module.__name__ + "." + cls.__name__


def make(cls):
    p = path(cls)
    return p.split(".")[2]


def model_type(cls):
    p = path(cls)
    return p.split(".")[4]


def backend_str(backend: MinerTypes) -> str:
    match backend:
        case MinerTypes.ANTMINER:
            return "Stock Firmware Antminers"
        case MinerTypes.AURADINE:
            return "Stock Firmware Auradine Miners"
        case MinerTypes.AVALONMINER:
            return "Stock Firmware Avalonminers"
        case MinerTypes.VNISH:
            return "Vnish Firmware Miners"
        case MinerTypes.EPIC:
            return "ePIC Firmware Miners"
        case MinerTypes.BRAIINS_OS:
            return "BOS+ Firmware Miners"
        case MinerTypes.HIVEON:
            return "HiveOS Firmware Miners"
        case MinerTypes.INNOSILICON:
            return "Stock Firmware Innosilicons"
        case MinerTypes.WHATSMINER:
            return "Stock Firmware Whatsminers"
        case MinerTypes.GOLDSHELL:
            return "Stock Firmware Goldshells"
        case MinerTypes.LUX_OS:
            return "LuxOS Firmware Miners"
        case MinerTypes.EPIC:
            return "ePIC Firmware Miners"


def create_url_str(mtype: str):
    return (
        mtype.lower()
        .replace(" ", "-")
        .replace("(", "")
        .replace(")", "")
        .replace("+", "_1")
    )


HEADER_FORMAT = "# pyasic\n## {} Models\n\n"
MINER_HEADER_FORMAT = "## {}\n"
DATA_FORMAT = """::: {}
    handler: python
    options:
        show_root_heading: false
        heading_level: 4

"""
SUPPORTED_TYPES_HEADER = """# pyasic
## Supported Miners

Supported miner types are here on this list.  If your miner (or miner version) is not on this list, please feel free to [open an issue on GitHub](https://github.com/UpstreamData/pyasic/issues) to get it added.

##### pyasic currently supports the following miners and subtypes:
<style>
details {
    margin:0px;
    padding-top:0px;
    padding-bottom:0px;
}
</style>
"""
BACKEND_TYPE_HEADER = """
<details>
<summary>{}:</summary>
    <ul>"""

MINER_TYPE_HEADER = """
        <details>
            <summary>{} Series:</summary>
                <ul>"""

MINER_DETAILS = """
                    <li><a href="../{}/{}#{}">{}</a></li>"""

MINER_TYPE_CLOSER = """
                </ul>
        </details>"""
BACKEND_TYPE_CLOSER = """
    </ul>
</details>"""

m_data = {}


for m in MINER_CLASSES:
    for t in MINER_CLASSES[m]:
        if t is not None:
            miner = MINER_CLASSES[m][t]
            if make(miner) not in m_data:
                m_data[make(miner)] = {}
            if model_type(miner) not in m_data[make(miner)]:
                m_data[make(miner)][model_type(miner)] = []
            m_data[make(miner)][model_type(miner)].append(miner)


async def create_directory_structure(directory, data):
    if not os.path.exists(directory):
        os.makedirs(directory)

    for key, value in data.items():
        subdirectory = os.path.join(directory, key)
        if isinstance(value, dict):
            await create_directory_structure(subdirectory, value)
        elif isinstance(value, list):
            file_path = os.path.join(subdirectory + ".md")

            with open(file_path, "w") as file:
                file.write(HEADER_FORMAT.format(key))
                for item in value:
                    header = await item("1.1.1.1").get_model()
                    file.write(MINER_HEADER_FORMAT.format(header))
                    file.write(DATA_FORMAT.format(path(item)))


async def create_supported_types(directory):
    with open(os.path.join(directory, "supported_types.md"), "w") as file:
        file.write(SUPPORTED_TYPES_HEADER)
        for mback in MINER_CLASSES:
            backend_types = {}
            file.write(BACKEND_TYPE_HEADER.format(backend_str(mback)))
            for mtype in MINER_CLASSES[mback]:
                if mtype is None:
                    continue
                m = MINER_CLASSES[mback][mtype]
                if model_type(m) not in backend_types:
                    backend_types[model_type(m)] = []
                backend_types[model_type(m)].append(m)

            for mtype in backend_types:
                file.write(MINER_TYPE_HEADER.format(mtype))
                for minstance in backend_types[mtype]:
                    model = await minstance("1.1.1.1").get_model()
                    file.write(
                        MINER_DETAILS.format(
                            make(minstance), mtype, create_url_str(model), model
                        )
                    )
                file.write(MINER_TYPE_CLOSER)
            file.write(BACKEND_TYPE_CLOSER)


root_directory = os.path.join(os.getcwd(), "miners")
asyncio.run(create_directory_structure(root_directory, m_data))
asyncio.run(create_supported_types(root_directory))
