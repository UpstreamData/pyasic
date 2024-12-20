from __future__ import annotations

from abc import ABC, abstractmethod

from pydantic import BaseModel
from typing_extensions import Self

from .unit.base import AlgoHashRateUnitType, GenericUnit


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

    def __add__(self, other: Self | int | float) -> Self:
        if isinstance(other, AlgoHashRateType):
            return self.__class__(
                rate=self.rate + other.into(self.unit).rate, unit=self.unit
            )
        return self.__class__(rate=self.rate + other, unit=self.unit)

    def __sub__(self, other: Self | int | float) -> Self:
        if isinstance(other, AlgoHashRateType):
            return self.__class__(
                rate=self.rate - other.into(self.unit).rate, unit=self.unit
            )
        return self.__class__(rate=self.rate - other, unit=self.unit)

    def __truediv__(self, other: Self | int | float) -> Self:
        if isinstance(other, AlgoHashRateType):
            return self.__class__(
                rate=self.rate / other.into(self.unit).rate, unit=self.unit
            )
        return self.__class__(rate=self.rate / other, unit=self.unit)

    def __floordiv__(self, other: Self | int | float) -> Self:
        if isinstance(other, AlgoHashRateType):
            return self.__class__(
                rate=self.rate // other.into(self.unit).rate, unit=self.unit
            )
        return self.__class__(rate=self.rate // other, unit=self.unit)

    def __mul__(self, other: Self | int | float) -> Self:
        if isinstance(other, AlgoHashRateType):
            return self.__class__(
                rate=self.rate * other.into(self.unit).rate, unit=self.unit
            )
        return self.__class__(rate=self.rate * other, unit=self.unit)


class GenericHashrate(AlgoHashRateType):
    def into(self, other: GenericUnit):
        return self.__class__(
            rate=self.rate / (other.value / self.unit.value), unit=other
        )
