import asyncio

from tools.cfg_util.record.layout import record_window

from miners.miner_factory import MinerFactory

from typing import List, Dict

(RECORDING, PAUSING, PAUSED, RESUMING, STOPPING, DONE) = range(6)


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class RecordingManager(metaclass=Singleton):
    _instance = None

    def __init__(self):
        self.state = DONE
        self.data: Dict[str:list] = {}
        self.miners = []
        self.output_file = None
        self.interval = 10

    async def _check_pause(self):
        if self.state == PAUSING:
            self.state = PAUSED
            record_window["record_status"].update("Paused.")
            while not self.state == RESUMING and not self.state == STOPPING:
                await asyncio.sleep(0.1)
            record_window["record_status"].update("Recording...")

    async def _record_loop(self):
        while True:
            await self._check_pause()

            if self.state == STOPPING:
                break

            tasks = []
            for miner in self.miners:
                tasks.append(miner.get_data())

            for complete in asyncio.as_completed(tasks):
                data = await complete
                print(data)
                self.data[data.ip].append(data)
            for i in range(self.interval * 10):
                await self._check_pause()
                if self.state == STOPPING:
                    break
                await asyncio.sleep(0.1)

        self.state = DONE
        record_window["record_status"].update("Writing to file...")
        await self.write_output()
        record_window["record_status"].update("")

    async def write_output(self):
        from pprint import pprint

        pprint(self.data)

    async def record(self, ips: List[str], output_file: str, interval: int = 10):
        for ip in ips:
            self.data[ip] = []
        self.output_file = output_file
        self.interval = interval
        self.state = RECORDING
        record_window["record_status"].update("Recording...")
        async for miner in MinerFactory().get_miner_generator(ips):
            self.miners.append(miner)
            print(miner)

        asyncio.create_task(self._record_loop())

    async def pause(self):
        self.state = PAUSING
        record_window["record_status"].update("Pausing...")

    async def resume(self):
        self.state = RESUMING
        record_window["record_status"].update("Resuming...")

    async def stop(self):
        self.state = STOPPING
        record_window["record_status"].update("Stopping...")
