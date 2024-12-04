from pyasic.config.base import MinerConfigValue


class MiningPreset(MinerConfigValue):
    name: str | None = None
    power: int | None = None
    hashrate: int | None = None
    tuned: bool | None = None
    modded_psu: bool = False

    def as_vnish(self) -> dict:
        if self.name is not None:
            return {"preset": self.name}
        return {}
