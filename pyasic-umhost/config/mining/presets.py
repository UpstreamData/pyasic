from pyasic.config.base import MinerConfigValue


class MiningPreset(MinerConfigValue):
    name: str | None = None
    power: int | None = None
    hashrate: int | None = None
    tuned: bool | None = None
    modded_psu: bool | None = None
    frequency: int | None = None
    voltage: float | None = None

    def as_vnish(self) -> dict:
        if self.name is not None:
            return {"preset": self.name}
        return {}

    @classmethod
    def from_vnish(cls, web_preset: dict):
        name = web_preset["name"]
        hr_power_split = web_preset["pretty"].split("~")
        if len(hr_power_split) == 1:
            power = None
            hashrate = None
        else:
            power = hr_power_split[0].replace("watt", "").strip()
            hashrate = (
                hr_power_split[1]
                .replace("TH", "")
                .replace("GH", "")
                .replace("MH", "")
                .replace(" LC", "")
                .strip()
            )
        tuned = web_preset["status"] == "tuned"
        modded_psu = web_preset["modded_psu_required"]
        return cls(
            name=name,
            power=power,
            hashrate=hashrate,
            tuned=tuned,
            modded_psu=modded_psu,
        )

    @classmethod
    def from_luxos(cls, profile: dict):
        return cls(
            name=profile["Profile Name"],
            power=profile["Watts"],
            hashrate=round(profile["Hashrate"]),
            tuned=profile["IsTuned"],
            frequency=profile["Frequency"],
            voltage=profile["Voltage"],
        )
