import logging
import toml

from miners.bosminer import BOSMiner
from config.bos import general_config_convert_bos


class BOSMinerS9(BOSMiner):
    def __init__(self, ip: str) -> None:
        super().__init__(ip)
        self.model = "S9"
        self.api_type = "BOSMiner"

    def __repr__(self) -> str:
        return f"BOSminerS9: {str(self.ip)}"

    async def send_config(self, yaml_config) -> None:
        """Configures miner with yaml config."""
        logging.debug(f"{self}: Sending config.")
        conf = await general_config_convert_bos(yaml_config)
        toml_conf = toml.dumps(conf)
        conf["format"]["model"] = "Antminer S9"
        async with (await self._get_ssh_connection()) as conn:
            logging.debug(f"{self}: Opening SFTP connection.")
            async with conn.start_sftp_client() as sftp:
                logging.debug(f"{self}: Opening config file.")
                async with sftp.open('/etc/bosminer.toml', 'w+') as file:
                    await file.write(toml_conf)
            logging.debug(f"{self}: Restarting BOSMiner")
            await conn.run("/etc/init.d/bosminer restart")
