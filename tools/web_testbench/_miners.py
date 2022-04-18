from ipaddress import ip_address
import asyncio
import os
import logging

from network import ping_miner
from miners.miner_factory import MinerFactory
from miners.antminer.S9.bosminer import BOSMinerS9
from tools.web_testbench.connections import ConnectionManager
from tools.web_testbench.feeds import get_local_versions

REFERRAL_FILE_S9 = os.path.join(os.path.dirname(__file__), "files", "referral.ipk")
UPDATE_FILE_S9 = os.path.join(os.path.dirname(__file__), "files", "update.tar")
CONFIG_FILE = os.path.join(os.path.dirname(__file__), "files", "config.toml")

# static states
(START, UNLOCK, INSTALL, UPDATE, REFERRAL, DONE) = range(6)


class TestbenchMiner:
    def __init__(self, host: ip_address):
        self.host = host
        self.state = START
        self.latest_version = None

    async def get_bos_version(self):
        miner = await MinerFactory().get_miner(self.host)
        result = await miner.send_ssh_command("cat /etc/bos_version")
        version_base = result.stdout
        version_base = version_base.strip()
        version_base = version_base.split("-")
        version = version_base[-2]
        return version

    async def add_to_output(self, message):
        await ConnectionManager().broadcast_json(
            {"IP": str(self.host), "text": str(message).replace("\r", "") + "\n"}
        )
        return

    async def remove_from_cache(self):
        if self.host in MinerFactory().miners.keys():
            MinerFactory().miners.remove(self.host)

    async def wait_for_disconnect(self):
        await self.add_to_output("Waiting for disconnect...")
        while await ping_miner(self.host):
            await asyncio.sleep(1)

    async def install_start(self):
        await ConnectionManager().broadcast_json(
            {"IP": str(self.host), "Light": "hide"}
        )
        if not await ping_miner(self.host, 80):
            await self.add_to_output("Waiting for miner connection...")
            return
        await self.remove_from_cache()
        miner = await MinerFactory().get_miner(self.host)
        await self.add_to_output("Found miner: " + str(miner))
        if isinstance(miner, BOSMinerS9):
            if await self.get_bos_version() == self.latest_version:
                await self.add_to_output(
                    f"Already running the latest version of BraiinsOS, {self.latest_version}, configuring."
                )
                self.state = REFERRAL
                return
            await self.add_to_output("Already running BraiinsOS, updating.")
            self.state = UPDATE
            return
        if await ping_miner(self.host, 22):
            await self.add_to_output("Miner is unlocked, installing.")
            self.state = INSTALL
            return
        await self.add_to_output("Miner needs unlock, unlocking.")
        self.state = UNLOCK

    async def install_unlock(self):
        if await self.ssh_unlock():
            await self.add_to_output("Unlocked miner, installing.")
            self.state = INSTALL
            return
        await self.add_to_output("Failed to unlock miner, please pin reset.")
        self.state = START
        await self.wait_for_disconnect()

    async def ssh_unlock(self):
        proc = await asyncio.create_subprocess_shell(
            f'{os.path.join(os.path.dirname(__file__), "files", "asicseer_installer.exe")} -p -f {str(self.host)} root',
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await proc.communicate()
        if str(stdout).find("webUI") != -1:
            return False
        return True

    async def fix_file_exists_bug(self):
        miner = await MinerFactory().get_miner(self.host)
        await miner.send_ssh_command(
            "rm /lib/ld-musl-armhf.so.1; rm /usr/lib/openssh/sftp-server; rm /usr/sbin/fw_printenv"
        )

    async def do_install(self):
        error = False
        proc = await asyncio.create_subprocess_shell(
            f'{os.path.join(os.path.dirname(__file__), "files", "bos-toolbox", "bos-toolbox.bat")} install {str(self.host)} --no-keep-pools --psu-power-limit 900 --no-nand-backup --feeds-url file:./feeds/',
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        # get stdout of the install
        while True:
            try:
                stdout = await proc.stderr.readuntil(b"\r")
            except asyncio.exceptions.IncompleteReadError:
                break
            stdout_data = stdout.decode("utf-8").strip()
            if "ERROR:File" in stdout_data:
                error = True
            await self.add_to_output(stdout_data)
            if stdout == b"":
                break
        await proc.wait()
        while not await ping_miner(self.host):
            await asyncio.sleep(3)
        await asyncio.sleep(5)
        if error:
            await self.add_to_output("Encountered error, attempting to fix.")
            await self.fix_file_exists_bug()
            self.state = START
            return
        await self.add_to_output("Install complete, configuring.")
        self.state = REFERRAL

    async def install_update(self):
        await self.add_to_output("Updating miner...")
        await self.remove_from_cache()
        miner = await MinerFactory().get_miner(self.host)
        try:
            await miner.send_file(UPDATE_FILE_S9, "/tmp/firmware.tar")
            await miner.send_ssh_command("sysupgrade /tmp/firmware.tar")
        except Exception as e:
            logging.warning(f"{str(self.host)} Exception: {e}")
            await self.add_to_output("Failed to update, restarting.")
            self.state = START
            return
        await asyncio.sleep(10)
        await self.add_to_output("Update complete, configuring.")
        self.state = REFERRAL

    async def install_referral(self):
        while not await ping_miner(self.host):
            await asyncio.sleep(1)
        miner = await MinerFactory().get_miner(self.host)
        try:
            await miner.send_file(REFERRAL_FILE_S9, "/tmp/referral.ipk")
            await miner.send_file(CONFIG_FILE, "/etc/bosminer.toml")
            await miner.send_ssh_command(
                "opkg install /tmp/referral.ipk && /etc/init.d/bosminer restart"
            )
        except Exception as e:
            await self.add_to_output(
                "Failed to add referral and configure, restarting."
            )
            self.state = START
            return
        await asyncio.sleep(5)
        await self.add_to_output("Configuration complete.")
        self.state = DONE

    async def get_web_data(self):
        miner = await MinerFactory().get_miner(self.host)

        if not isinstance(miner, BOSMinerS9):
            await self.add_to_output("Miner type changed, restarting.")
            self.state = START
            return
        try:
            all_data = await miner.api.multicommand("devs", "temps", "fans")

            devs_raw = all_data["devs"][0]
            temps_raw = all_data["temps"][0]
            fans_raw = all_data["fans"][0]

            # parse temperature data
            temps_data = {}
            for board in range(len(temps_raw["TEMPS"])):
                temps_data[f"board_{temps_raw['TEMPS'][board]['ID']}"] = {}
                temps_data[f"board_{temps_raw['TEMPS'][board]['ID']}"][
                    "Board"
                ] = temps_raw["TEMPS"][board]["Board"]
                temps_data[f"board_{temps_raw['TEMPS'][board]['ID']}"][
                    "Chip"
                ] = temps_raw["TEMPS"][board]["Chip"]

            if len(temps_data.keys()) < 3:
                for board in [6, 7, 8]:
                    if f"board_{board}" not in temps_data.keys():
                        temps_data[f"board_{board}"] = {"Chip": 0, "Board": 0}

            # parse individual board and chip temperature data
            for board in temps_data.keys():
                if "Board" not in temps_data[board].keys():
                    temps_data[board]["Board"] = 0
                if "Chip" not in temps_data[board].keys():
                    temps_data[board]["Chip"] = 0

            # parse hashrate data
            hr_data = {}
            for board in range(len(devs_raw["DEVS"])):
                hr_data[f"board_{devs_raw['DEVS'][board]['ID']}"] = {}
                hr_data[f"board_{devs_raw['DEVS'][board]['ID']}"]["HR"] = round(
                    devs_raw["DEVS"][board]["MHS 5s"] / 1000000, 2
                )

            # parse fan data
            fans_data = {}
            for fan in range(len(fans_raw["FANS"])):
                fans_data[f"fan_{fans_raw['FANS'][fan]['ID']}"] = {}
                fans_data[f"fan_{fans_raw['FANS'][fan]['ID']}"]["RPM"] = fans_raw[
                    "FANS"
                ][fan]["RPM"]

            # set the miner data
            miner_data = {
                "IP": str(self.host),
                "Light": "show",
                "Fans": fans_data,
                "HR": hr_data,
                "Temps": temps_data,
            }

            # return stats
            return miner_data
        except:
            return

    async def install_done(self):
        await self.add_to_output("Waiting for disconnect...")
        try:
            while await ping_miner(self.host) and self.state == DONE:
                data = await self.get_web_data()
                await ConnectionManager().broadcast_json(data)
                await asyncio.sleep(1)
        except:
            self.state = START
            await self.add_to_output("Miner disconnected, waiting for new miner.")
            return
        self.state = START
        await self.add_to_output("Miner disconnected, waiting for new miner.")

    async def install_loop(self):
        self.latest_version = sorted(await get_local_versions(), reverse=True)[0]
        while True:
            if self.state == START:
                await self.install_start()
            if self.state == UNLOCK:
                await self.install_unlock()
            if self.state == INSTALL:
                await self.do_install()
            if self.state == UPDATE:
                await self.install_update()
            if self.state == REFERRAL:
                await self.install_referral()
            if self.state == DONE:
                await self.install_done()
