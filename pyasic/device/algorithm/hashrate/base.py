from __future__ import annotations

from typing import Any

from pydantic import BaseModel, field_serializer
from typing_extensions import Self

from .unit.base import GenericUnit


class AlgoHashRateType(BaseModel):
    unit: Any
    rate: float

    @field_serializer("unit")
    def serialize_unit(self, unit: Any) -> dict[str, object]:
        result: dict[str, object] = unit.model_dump()
        return result

    def into(self, other: Any) -> Self:
        if hasattr(self.unit, "value") and hasattr(other, "value"):
            return self.__class__(
                rate=self.rate / (other.value / self.unit.value), unit=other
            )
        return self

    def auto_unit(self) -> Self:
        if hasattr(self.unit, "H") and 1 < self.rate / int(self.unit.H) < 1000:
            return self.into(self.unit.H)
        if hasattr(self.unit, "MH") and 1 < self.rate / int(self.unit.MH) < 1000:
            return self.into(self.unit.MH)
        if hasattr(self.unit, "GH") and 1 < self.rate / int(self.unit.GH) < 1000:
            return self.into(self.unit.GH)
        if hasattr(self.unit, "TH") and 1 < self.rate / int(self.unit.TH) < 1000:
            return self.into(self.unit.TH)
        if hasattr(self.unit, "PH") and 1 < self.rate / int(self.unit.PH) < 1000:
            return self.into(self.unit.PH)
        if hasattr(self.unit, "EH") and 1 < self.rate / int(self.unit.EH) < 1000:
            return self.into(self.unit.EH)
        if hasattr(self.unit, "ZH") and 1 < self.rate / int(self.unit.ZH) < 1000:
            return self.into(self.unit.ZH)
        return self

    def __float__(self) -> float:
        return float(self.rate)

    def __int__(self) -> int:
        return int(self.rate)

    def __repr__(self) -> str:
        return f"{self.rate} {str(self.unit)}"

    def __round__(self, n: int | None = None) -> float:
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
    rate: float = 0
    unit: GenericUnit = GenericUnit.H

    def into(self, other: GenericUnit) -> Self:
        return self.__class__(
            rate=self.rate / (other.value / self.unit.value), unit=other
        )
