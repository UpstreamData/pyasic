import asyncio

from tools.cfg_util.record.pdf import generate_pdf

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
        self.record_window = None

    async def _check_pause(self):
        if self.state == PAUSING:
            self.state = PAUSED
            self.record_window["record_status"].update("Paused.")
            while not self.state == RESUMING and not self.state == STOPPING:
                await asyncio.sleep(0.1)
            self.record_window["record_status"].update("Recording...")

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
        self.record_window["record_status"].update(
            "Writing to file (this could take a minute)..."
        )
        await asyncio.sleep(0.5)
        await asyncio.create_task(self.write_output())
        self.record_window["record_status"].update("")

    async def write_output(self):
        await generate_pdf(self.data, self.output_file)

    async def record(
        self, ips: List[str], output_file: str, record_window, interval: int = 10
    ):
        self.record_window = record_window
        for ip in ips:
            self.data[ip] = []
        self.output_file = output_file
        self.interval = interval
        self.state = RECORDING
        self.record_window["record_status"].update("Recording...")
        async for miner in MinerFactory().get_miner_generator(ips):
            self.miners.append(miner)

        asyncio.create_task(self._record_loop())

    async def pause(self):
        self.state = PAUSING
        self.record_window["record_status"].update("Pausing...")

    async def resume(self):
        self.state = RESUMING
        self.record_window["record_status"].update("Resuming...")

    async def stop(self):
        self.state = STOPPING
        self.record_window["record_status"].update("Stopping...")
