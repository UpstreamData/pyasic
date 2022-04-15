import aiohttp
import shutil
import aiofiles
import asyncio
from bs4 import BeautifulSoup
import re
import os
import logging


async def get_latest_version(session):
    feeds_url = "http://feeds.braiins-os.com"

    async with session.get(feeds_url) as resp:
        data = await resp.read()

    soup = BeautifulSoup(data, "html.parser")

    versions = []

    for link in soup.find_all("td", {"class": "link"}):
        link_title = link.text.strip("/")
        if re.match("(\d+)\.(\d+)(\.\d+)?", link_title):
            versions.append(link_title)

    versions = sorted(versions, reverse=True)

    latest_version = versions[0]
    return latest_version


async def get_feeds_file(session, version):
    feeds_url = "http://feeds.braiins-os.com"

    async with session.get(feeds_url + "/" + version) as resp:
        data = await resp.read()

    soup = BeautifulSoup(data, "html.parser")

    file = None

    for link in soup.find_all("a", href=True):
        href = link["href"]
        if re.match("braiins-os_am1-s9_ssh_.+\.tar.gz", href):
            if not href.endswith(".asc"):
                file = href

    if file:
        return file


async def get_update_file(session, version):
    feeds_url = "http://feeds.braiins-os.com"

    async with session.get(feeds_url + "/am1-s9") as resp:
        data = await resp.read()

    soup = BeautifulSoup(data, "html.parser")

    file = None

    for link in soup.find_all("a", href=True):
        href = link["href"]
        if re.match(f"firmware_(.+)-{version}-plus_arm_cortex-a9_neon\.tar", href):
            if not href.endswith(".asc"):
                file = href

    if file:
        return file


async def get_latest_update_file(session, update_file):
    update_file_loc = f"http://feeds.braiins-os.com/am1-s9/{update_file}"

    update_file_dir = os.path.join(os.path.dirname(__file__), "files", "update.tar")

    if os.path.exists(update_file_dir):
        os.remove(update_file_dir)

    async with session.get(update_file_loc) as update_file_data:
        if update_file_data.status == 200:
            f = await aiofiles.open(
                os.path.join(os.path.dirname(__file__), "files", "update.tar"),
                mode="wb",
            )
            await f.write(await update_file_data.read())
            await f.close()


async def get_latest_install_file(session, version, feeds_path, install_file):
    install_file_loc = f"http://feeds.braiins-os.com/{version}/{install_file}"
    feeds_file_path = os.path.join(feeds_path, "toolbox_bos_am1-s9")

    with open(feeds_file_path, "a+") as feeds_file:
        feeds_file.write(version + "\t" + install_file)

    install_file_folder = os.path.join(feeds_path, version)
    if os.path.exists(install_file_folder):
        shutil.rmtree(install_file_folder)
    os.mkdir(install_file_folder)

    async with session.get(install_file_loc) as install_file_data:
        if install_file_data.status == 200:
            f = await aiofiles.open(
                os.path.join(install_file_folder, install_file), mode="wb"
            )
            await f.write(await install_file_data.read())
            await f.close()


async def update_installer_files():
    feeds_path = os.path.join(
        os.path.dirname(__file__), "files", "bos-toolbox", "feeds"
    )
    feeds_versions = await get_local_versions()
    async with aiohttp.ClientSession() as session:
        version = await get_latest_version(session)

        if version not in feeds_versions:
            update_file = await get_update_file(session, version)
            install_file = await get_feeds_file(session, version)
            await get_latest_update_file(session, update_file)
            await get_latest_install_file(session, version, feeds_path, install_file)
        else:
            logging.info("Feeds are up to date.")


async def get_local_versions():
    feeds_versions = []
    feeds_path = os.path.join(
        os.path.dirname(__file__), "files", "bos-toolbox", "feeds"
    )
    if not os.path.exists(feeds_path):
        os.mkdir(feeds_path)

    feeds_file_path = os.path.join(feeds_path, "toolbox_bos_am1-s9")

    if not os.path.exists(feeds_file_path):
        feeds_file = open(feeds_file_path, "w+")
        feeds_file.close()

    with open(feeds_file_path) as feeds_file:
        for line in feeds_file.readlines():
            ver = line.strip().split("\t")[0]
            feeds_versions.append(ver)

    return feeds_versions



if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(update_installer_files())
