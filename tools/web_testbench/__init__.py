from ipaddress import ip_address
import asyncio
import os

from network import ping_miner
from miners.miner_factory import MinerFactory
from miners.antminer.S9.bosminer import BOSMinerS9
from tools.web_testbench._network import miner_network
from tools.web_testbench.app import ConnectionManager

REFERRAL_FILE_S9 = os.path.join(os.path.dirname(__file__), "files", "referral.ipk")
UPDATE_FILE_S9 = os.path.join(os.path.dirname(__file__), "files", "update.tar")
CONFIG_FILE = os.path.join(os.path.dirname(__file__), "files", "config.toml")


# static states
(START, UNLOCK, INSTALL, UPDATE, REFERRAL, DONE) = range(6)


class testbenchMiner:
    def __init__(self, host: ip_address):
        self.host = host
        self.state = START
        self.light = False

    async def fault_light(self):
        miner = await MinerFactory().get_miner(self.host)
        if self.light:
            await miner.fault_light_off()
        else:
            await miner.fault_light_on()

    async def add_to_output(self, message):
        await ConnectionManager().broadcast_json(
            {"IP": self.host, "text": str(message)}
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
        if not await ping_miner(self.host):
            return
        await self.remove_from_cache()
        miner = await MinerFactory().get_miner(self.host)
        await self.add_to_output("Found miner: " + miner)
        if isinstance(miner, BOSMinerS9):
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

    async def do_install(self):
        proc = await asyncio.create_subprocess_shell(
            f'{os.path.join(os.path.dirname(__file__), "files", "bos-toolbox", "bos-toolbox.bat")} install {str(self.host)} --no-keep-pools --psu-power-limit 900 --no-nand-backup --feeds-url file:./feeds/',
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        # get stdout of the install
        while True:
            stdout = await proc.stderr.readuntil(b"\r")
            await self.add_to_output(stdout)
            if stdout == b"":
                break
        await proc.wait()
        while not await ping_miner(self.host):
            await asyncio.sleep(3)
        await asyncio.sleep(5)
        await self.add_to_output("Install complete, configuring.")
        self.state = REFERRAL

    async def install_update(self):
        await self.remove_from_cache()
        miner = await MinerFactory().get_miner(self.host)
        try:
            await miner.send_file(UPDATE_FILE_S9, "/tmp/firmware.tar")
            await miner.send_ssh_command("sysupgrade /tmp/firmware.tar")
        except:
            await self.add_to_output("Failed to update, restarting.")
            self.state = START
            return
        await self.add_to_output("Update complete, configuring.")
        self.state = REFERRAL

    async def install_referral(self):
        miner = await MinerFactory().get_miner(self.host)
        if os.path.exists(REFERRAL_FILE_S9):
            try:
                await miner.send_file(REFERRAL_FILE_S9, "/tmp/referral.ipk")
                await miner.send_file(CONFIG_FILE, "/etc/bosminer.toml")

                await miner.send_ssh_command(
                    "opkg install /tmp/referral.ipk && /etc/init.d/bosminer restart"
                )
            except:
                await self.add_to_output(
                    "Failed to add referral and configure, restarting."
                )
                self.state = START
                return
        else:
            await self.add_to_output(
                "Failed to add referral and configure, restarting."
            )
            self.state = START
            return
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
                "IP": self.host,
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
        while await ping_miner(self.host) and self.state == DONE:
            await ConnectionManager().broadcast_json(await self.get_web_data())
            await asyncio.sleep(1)
        self.state = START

    async def install_loop(self):
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
