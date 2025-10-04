from pyasic import settings
from pyasic.ssh.base import BaseSSH


class BOSMinerSSH(BaseSSH):
    def __init__(self, ip: str) -> None:
        """
        Initialize a BOSMinerSSH instance.

        Args:
            ip (str): The IP address of the BOSMiner device.
        """
        super().__init__(ip)
        self.pwd = settings.get("default_bosminer_ssh_password", "root")

    async def get_board_info(self) -> str | None:
        """
        Retrieve information about the BOSMiner board.

        Returns:
            str: Information about the BOSMiner board.
        """
        return await self.send_command("bosminer model -d")

    async def fault_light_on(self) -> str | None:
        """
        Turn on the fault light of the BOSMiner device.

        Returns:
            str: Confirmation message after turning on the fault light.
        """
        return await self.send_command("miner fault_light on")

    async def fault_light_off(self) -> str | None:
        """
        Turn off the fault light of the BOSMiner device.

        Returns:
            str: Confirmation message after turning off the fault light.
        """
        return await self.send_command("miner fault_light off")

    async def restart_bosminer(self) -> str | None:
        """
        Restart the BOSMiner service on the device.

        Returns:
            str: Confirmation message after restarting the BOSMiner service.
        """
        return await self.send_command("/etc/init.d/bosminer restart")

    async def reboot(self) -> str | None:
        """
        Reboot the BOSMiner device.

        Returns:
            str: Confirmation message after initiating the reboot process.
        """
        return await self.send_command("/sbin/reboot")

    async def get_config_file(self) -> str | None:
        """
        Retrieve the configuration file of BOSMiner.

        Returns:
            str: Content of the BOSMiner configuration file.
        """
        return await self.send_command("cat /etc/bosminer.toml")

    async def get_network_config(self) -> str | None:
        """
        Retrieve the network configuration of the BOSMiner device.

        Returns:
            str: Content of the network configuration file.
        """
        return await self.send_command("cat /etc/config/network")

    async def get_hostname(self) -> str | None:
        """
        Retrieve the hostname of the BOSMiner device.

        Returns:
            str: Hostname of the BOSMiner device.
        """
        return await self.send_command("cat /proc/sys/kernel/hostname")

    async def get_led_status(self) -> str | None:
        """
        Retrieve the status of the LED on the BOSMiner device.

        Returns:
            str: Status of the LED.
        """
        return await self.send_command("cat /sys/class/leds/'Red LED'/delay_off")
