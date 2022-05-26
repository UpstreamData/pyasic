from ipaddress import ip_address
import asyncio
import os
import logging
import datetime

from network import ping_miner
from miners.miner_factory import MinerFactory
from miners.antminer import BOSMinerS9
from miners._backends.bosminer_old import BOSMinerOld  # noqa - Ignore access to _module
from miners.unknown import UnknownMiner
from tools.web_testbench.connections import ConnectionManager
from tools.web_testbench.feeds import get_local_versions
from settings import NETWORK_PING_TIMEOUT as PING_TIMEOUT
import sys

REFERRAL_FILE_S9 = os.path.join(os.path.dirname(__file__), "files", "referral.ipk")
UPDATE_FILE_S9 = os.path.join(os.path.dirname(__file__), "files", "update.tar")
CONFIG_FILE = os.path.join(os.path.dirname(__file__), "files", "config.toml")

# static states
(START, UNLOCK, INSTALL, UPDATE, REFERRAL, DONE, ERROR) = range(7)

if (
    sys.version_info[0] == 3
    and sys.version_info[1] >= 8
    and sys.platform.startswith("win")
):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class Miners(metaclass=Singleton):
    def __init__(self):
        self.miners = []

    def get_count(self):
        return len(self.miners)

    def __add__(self, other):
        if other not in self.miners:
            self.miners.append(other)

    def __sub__(self, other):
        if other in self.miners:
            self.miners.remove(other)


class TestbenchMiner:
    def __init__(self, host: ip_address):
        self.host = host
        self.state = START
        self.latest_version = None
        self.start_time = None

    async def get_bos_version(self):
        miner = await MinerFactory().get_miner(self.host)
        result = await miner.send_ssh_command("cat /etc/bos_version")
        version_base = result
        version_base = version_base.strip()
        version_base = version_base.split("-")
        version = version_base[-2]
        return version

    def get_online_time(self):
        online_time = "0:00:00"
        if self.start_time:
            online_time = str(datetime.datetime.now() - self.start_time).split(".")[0]
        return online_time

    async def add_to_output(self, message):
        data = {
            "IP": str(self.host),
            "text": str(message).replace("\r", "") + "\n",
            "Light": "hide",
            "online": self.get_online_time(),
        }

        await ConnectionManager().broadcast_json(data)
        return

    async def remove_from_cache(self):
        if self.host in MinerFactory().miners.keys():
            del MinerFactory().miners[self.host]

    async def wait_for_disconnect(self, wait_time: int = 1):
        await self.add_to_output("Waiting for disconnect...")
        while await ping_miner(self.host):
            await asyncio.sleep(wait_time)
        self.state = START

    async def install_start(self):
        try:
            if not await ping_miner(self.host, 80):
                data = {
                    "IP": str(self.host),
                    "Count": Miners().get_count(),
                }
                await ConnectionManager().broadcast_json(data)
                await self.add_to_output("Waiting for miner connection...")
                miners = Miners()
                miners -= self.host
                return
        except asyncio.exceptions.TimeoutError:
            await self.add_to_output("Waiting for miner connection...")
            miners = Miners()
            miners -= self.host
            return
        self.start_time = datetime.datetime.now()
        await ConnectionManager().broadcast_json(
            {"IP": str(self.host), "Light": "hide", "online": self.get_online_time()}
        )
        miners = Miners()
        miners += self.host
        await self.remove_from_cache()
        miner = await MinerFactory().get_miner(self.host)
        await self.add_to_output("Found miner: " + str(miner))
        if isinstance(miner, BOSMinerOld):
            await self.add_to_output(
                f"Miner is running non-plus Braiins OS, attempting upgrade."
            )
            result = await miner.update_to_plus()
            if result:
                await self.remove_from_cache()
                self.state = START
                return

        if isinstance(miner, BOSMinerS9):
            try:
                if await self.get_bos_version() == self.latest_version:
                    await self.add_to_output(
                        f"Already running the latest version of BraiinsOS, {self.latest_version}, configuring."
                    )
                    self.state = REFERRAL
                    return
            except AttributeError as e:
                logging.warning(e)
                return
            await self.add_to_output("Already running BraiinsOS, updating.")
            self.state = UPDATE
            return
        elif isinstance(miner, UnknownMiner):
            await self.add_to_output("Unknown Miner found, attempting to fix.")
            try:
                async with (
                    await miner._get_ssh_connection()  # noqa - Ignore access to _function
                ) as conn:
                    result = await conn.run("opkg update && opkg upgrade firmware")
            except:
                await self.add_to_output("Fix failed, please manually reset miner.")
                self.state = ERROR
                return
            if result:
                await self.add_to_output("Fix may have worked, retrying.")
                await asyncio.sleep(10)
                self.state = START
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
        await self.add_to_output("Running install...")
        error = None
        proc = await asyncio.create_subprocess_shell(
            f'{os.path.join(os.path.dirname(__file__), "files", "bos-toolbox", "bos-toolbox.bat")} install {str(self.host)} --no-keep-pools --psu-power-limit 900 --no-nand-backup --feeds-url file:./feeds/',
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            stdin=asyncio.subprocess.PIPE,
        )
        # get stdout of the install
        stdout = None
        await self.add_to_output("Getting output...")
        while True:
            try:
                stdout = await asyncio.wait_for(proc.stderr.readuntil(b"\r"), 20)
            except asyncio.exceptions.IncompleteReadError:
                break
            except asyncio.exceptions.TimeoutError:
                if not stdout:
                    await self.add_to_output(
                        "Miner encountered an error when installing, attempting to re-unlock.  If this fails, you may need to factory reset the miner."
                    )
                    self.state = UNLOCK
                    proc.kill()
                    return
                continue
            stdout_data = stdout.decode("utf-8").strip()
            if "ERROR:File" in stdout_data:
                error = "FILE"
            if "ERROR:Auth" in stdout_data:
                error = "AUTH"
                proc.kill()
            await self.add_to_output(stdout_data)
            if stdout == b"":
                break
        await self.add_to_output("Waiting for process to complete...")
        await proc.wait()
        if not error:
            await self.add_to_output("Waiting for miner to finish rebooting...")
            while not await ping_miner(self.host):
                await asyncio.sleep(3)
            await asyncio.sleep(5)
        if error == "FILE":
            await self.add_to_output("Encountered error, attempting to fix.")
            await self.fix_file_exists_bug()
            self.state = START
            return
        elif error == "AUTH":
            await self.add_to_output("Encountered unlock error, please pin reset.")
            self.state = ERROR
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
        except Exception:
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
            all_data = await miner.api.multicommand(
                "devs", "temps", "fans", "tunerstatus"
            )

            devs_raw = all_data["devs"][0]
            temps_raw = all_data["temps"][0]
            fans_raw = all_data["fans"][0]
            tunerstatus_raw = all_data["tunerstatus"][0]

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

            if len(hr_data.keys()) < 3:
                for board in [6, 7, 8]:
                    if f"board_{board}" not in hr_data.keys():
                        hr_data[f"board_{board}"] = {"HR": 0}

            # parse fan data
            fans_data = {}
            for fan in range(len(fans_raw["FANS"])):
                fans_data[f"fan_{fans_raw['FANS'][fan]['ID']}"] = {}
                fans_data[f"fan_{fans_raw['FANS'][fan]['ID']}"]["RPM"] = fans_raw[
                    "FANS"
                ][fan]["RPM"]

            # parse tuner data
            tuner_data = {}
            if tunerstatus_raw:
                for board in tunerstatus_raw["TUNERSTATUS"][0]["TunerChainStatus"]:
                    tuner_data[f"board_{board['HashchainIndex']}"] = {
                        "power_limit": board["PowerLimitWatt"],
                        "real_power": board["ApproximatePowerConsumptionWatt"],
                        "status": board["Status"],
                    }

            if len(tuner_data.keys()) < 3:
                for board in [6, 7, 8]:
                    if f"board_{board}" not in tuner_data.keys():
                        temps_data[f"board_{board}"] = {
                            "power_limit": 0,
                            "real_power": 0,
                            "status": "ERROR: No board found!",
                        }

            # set the miner data
            miner_data = {
                "IP": str(self.host),
                "Light": "show",
                "Fans": fans_data,
                "HR": hr_data,
                "Temps": temps_data,
                "online": self.get_online_time(),
                "Tuner": tuner_data,
                "Count": Miners().get_count(),
            }

            # return stats
            return miner_data
        except:
            return {
                "IP": str(self.host),
                "Light": "show",
                "Fans": {
                    "fan_0": {"RPM": 0},
                    "fan_1": {"RPM": 0},
                    "fan_2": {"RPM": 0},
                    "fan_3": {"RPM": 0},
                },
                "HR": {
                    "board_6": {"HR": 0},
                    "board_7": {"HR": 0},
                    "board_8": {"HR": 0},
                },
                "Temps": {
                    "board_8": {"Board": 0, "Chip": 0},
                    "board_6": {"Chip": 0, "Board": 0},
                    "board_7": {"Chip": 0, "Board": 0},
                },
                "online": self.get_online_time(),
                "Tuner": {
                    "board_6": {"power_limit": 275, "real_power": 0, "status": "None"},
                    "board_7": {"power_limit": 275, "real_power": 0, "status": "None"},
                    "board_8": {"power_limit": 275, "real_power": 0, "status": "None"},
                },
                "Count": Miners().get_count(),
            }

    async def install_done(self):
        await self.add_to_output("Waiting for disconnect...")
        try:
            while (
                await asyncio.wait_for(ping_miner(self.host), PING_TIMEOUT + 3)
                and self.state == DONE
            ):
                try:
                    data = await self.get_web_data()
                except:
                    data = {
                        "IP": str(self.host),
                        "Light": "show",
                        "online": self.get_online_time(),
                        "Count": Miners().get_count(),
                    }
                    print(f"Getting data failed: {self.host}")

                try:
                    await ConnectionManager().broadcast_json(data)
                except:
                    print(f"Sending data failed: {self.host}")

                await asyncio.sleep(1)
        except:
            self.state = START
            await self.add_to_output("Miner disconnected, waiting for new miner.")
            self.start_time = None
            return
        self.state = START
        await self.add_to_output("Miner disconnected, waiting for new miner.")
        self.start_time = None

    async def install_loop(self):
        self.latest_version = sorted(await get_local_versions(), reverse=True)[0]
        while True:
            try:
                if self.state == START:
                    self.start_time = None
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
                if self.state == ERROR:
                    await self.wait_for_disconnect(wait_time=5)
            except GeneratorExit as E:
                logging.error(f"{self.host}: {E}")
                await self.add_to_output(f"Error: {E}")
            except RuntimeError as E:
                logging.error(f"{self.host}: {E}")
                await self.add_to_output(f"Error: {E}")
                asyncio.create_task(self.install_loop())
                return
            except Exception as E:
                logging.error(f"{self.host}: {E}")
                await self.add_to_output(f"Error: {E}")
