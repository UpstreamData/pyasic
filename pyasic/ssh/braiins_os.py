from pyasic import settings
from pyasic.ssh.base import BaseSSH


class BOSMinerSSH(BaseSSH):
    def __init__(self, ip: str):
        super().__init__(ip)
        self.pwd = settings.get("default_bosminer_ssh_password", "root")

    async def get_board_info(self):
        return await self.send_command("bosminer model -d")

    async def fault_light_on(self):
        return await self.send_command("miner fault_light on")

    async def fault_light_off(self):
        return await self.send_command("miner fault_light off")

    async def restart_bosminer(self):
        return await self.send_command("/etc/init.d/bosminer restart")

    async def reboot(self):
        return await self.send_command("/sbin/reboot")

    async def get_config_file(self):
        return await self.send_command("cat /etc/bosminer.toml")

    async def get_network_config(self):
        return await self.send_command("cat /etc/config/network")

    async def get_hostname(self):
        return await self.send_command("cat /proc/sys/kernel/hostname")

    async def get_led_status(self):
        return await self.send_command("cat /sys/class/leds/'Red LED'/delay_off")
