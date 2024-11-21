from abc import ABC, abstractmethod

from pydantic import BaseModel

from .unit.base import AlgoHashRateUnitType


class AlgoHashRateType(BaseModel, ABC):
    unit: AlgoHashRateUnitType
    rate: float

    @abstractmethod
    def into(self, other: "AlgoHashRateUnitType"):
        pass

    def __float__(self):
        return float(self.rate)

    def __int__(self):
        return int(self.rate)

    def __repr__(self):
        return f"{self.rate} {str(self.unit)}"

    def __round__(self, n: int = None):
        return round(self.rate, n)
