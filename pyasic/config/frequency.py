from pydantic import BaseModel, Field

from pyasic.config.base import MinerConfigValue


class FreqLevel(MinerConfigValue):
    """Уровень частоты (bitmain-freq-level / freq-level)."""

    level: str = Field(default="100")  # теперь Pydantic сам его примет

    @classmethod
    def default(cls) -> "FreqLevel":
        return cls()

    @classmethod
    def from_am_modern(cls, web_conf: dict) -> "FreqLevel":
        lvl = web_conf.get("bitmain-freq-level", "100")
        return cls(level=str(lvl))

    def as_am_modern(self) -> dict:
        return {"freq-level": self.level}
