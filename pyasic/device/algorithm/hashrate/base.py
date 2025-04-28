from __future__ import annotations

from abc import ABC, abstractmethod

from pydantic import BaseModel, field_serializer
from typing_extensions import Self

from .unit.base import AlgoHashRateUnitType, GenericUnit


class AlgoHashRateType(BaseModel, ABC):
    unit: AlgoHashRateUnitType
    rate: float

    @field_serializer("unit")
    def serialize_unit(self, unit: AlgoHashRateUnitType):
        return unit.model_dump()

    @abstractmethod
    def into(self, other: "AlgoHashRateUnitType"):
        pass

    def auto_unit(self):
        if 1 < self.rate // int(self.unit.H) < 1000:
            return self.into(self.unit.H)
        if 1 < self.rate // int(self.unit.MH) < 1000:
            return self.into(self.unit.MH)
        if 1 < self.rate // int(self.unit.GH) < 1000:
            return self.into(self.unit.GH)
        if 1 < self.rate // int(self.unit.TH) < 1000:
            return self.into(self.unit.TH)
        if 1 < self.rate // int(self.unit.PH) < 1000:
            return self.into(self.unit.PH)
        if 1 < self.rate // int(self.unit.EH) < 1000:
            return self.into(self.unit.EH)
        if 1 < self.rate // int(self.unit.ZH) < 1000:
            return self.into(self.unit.ZH)
        return self

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

    def __gt__(self, other):
        if isinstance(other, AlgoHashRateType):
            return self.rate > other.into(self.unit).rate
        raise ValueError("cannot compare with non AlgoHashRateType")

    def __lt__(self, other):
        if isinstance(other, AlgoHashRateType):
            return self.rate < other.into(self.unit).rate
        raise ValueError("cannot compare with non AlgoHashRateType")

    def __le__(self, other):
        if isinstance(other, AlgoHashRateType):
            return self.rate <= other.into(self.unit).rate
        raise ValueError("cannot compare with non AlgoHashRateType")

    def __ge__(self, other):
        if isinstance(other, AlgoHashRateType):
            return self.rate >= other.into(self.unit).rate
        raise ValueError("cannot compare with non AlgoHashRateType")

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
    rate: float = 0
    unit: GenericUnit = GenericUnit.H

    def into(self, other: GenericUnit):
        return self.__class__(
            rate=self.rate / (other.value / self.unit.value), unit=other
        )
