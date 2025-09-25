from collections.abc import Callable
from enum import Enum
from typing import Any
from urllib.parse import urlparse

from pydantic import BaseModel, computed_field, model_serializer
from typing_extensions import Self


class Scheme(Enum):
    STRATUM_V1 = "stratum+tcp"
    STRATUM_V2 = "stratum2+tcp"
    STRATUM_V1_SSL = "stratum+ssl"


class PoolUrl(BaseModel):
    scheme: Scheme
    host: str
    port: int
    pubkey: str | None = None

    @model_serializer
    def serialize(self):
        return str(self)

    def __str__(self) -> str:
        if self.scheme == Scheme.STRATUM_V2 and self.pubkey:
            return f"{self.scheme.value}://{self.host}:{self.port}/{self.pubkey}"
        else:
            return f"{self.scheme.value}://{self.host}:{self.port}"

    @classmethod
    def from_str(cls, url: str) -> Self | None:
        parsed_url = urlparse(url)
        if not parsed_url.hostname:
            return None
        if not parsed_url.scheme.strip() == "":
            scheme = Scheme(parsed_url.scheme)
        else:
            scheme = Scheme.STRATUM_V1
        host = parsed_url.hostname
        port = parsed_url.port
        if port is None:
            return None
        pubkey = parsed_url.path.lstrip("/") if scheme == Scheme.STRATUM_V2 else None
        return cls(scheme=scheme, host=host, port=port, pubkey=pubkey)


class PoolMetrics(BaseModel):
    """A dataclass to standardize pool metrics returned from miners.
    Attributes:

    accepted: Number of accepted shares.
    rejected: Number of rejected shares.
    get_failures: Number of failures in obtaining work from the pool.
    remote_failures: Number of failures communicating with the pool server.
    active: Indicates if the miner is connected to the stratum server.
    Alive : Indicates if a pool is alive.
    url: URL of the pool.
    index: Index of the pool.
    user: Username for the pool.
    pool_rejected_percent: Percentage of rejected shares by the pool.
    pool_stale_percent: Percentage of stale shares by the pool.
    """

    url: PoolUrl | None
    accepted: int | None = None
    rejected: int | None = None
    get_failures: int | None = None
    remote_failures: int | None = None
    active: bool | None = None
    alive: bool | None = None
    index: int | None = None
    user: str | None = None

    @computed_field  # type: ignore[prop-decorator]
    @property
    def pool_rejected_percent(self) -> float:  # noqa - Skip PyCharm inspection
        """Calculate and return the percentage of rejected shares"""
        if self.rejected is None or self.accepted is None:
            return 0.0
        return self._calculate_percentage(self.rejected, self.accepted + self.rejected)

    @computed_field  # type: ignore[prop-decorator]
    @property
    def pool_stale_percent(self) -> float:  # noqa - Skip PyCharm inspection
        """Calculate and return the percentage of stale shares."""
        if self.get_failures is None or self.accepted is None or self.rejected is None:
            return 0.0
        return self._calculate_percentage(
            self.get_failures, self.accepted + self.rejected
        )

    @staticmethod
    def _calculate_percentage(value: int, total: int) -> float:
        """Calculate the percentage."""
        if total == 0:
            return 0.0
        return (value / total) * 100

    def as_influxdb(self, key_root: str, level_delimiter: str = ".") -> str:
        def serialize_int(key: str, value: int) -> str:
            return f"{key}={value}"

        def serialize_float(key: str, value: float) -> str:
            return f"{key}={value}"

        def serialize_str(key: str, value: str) -> str:
            return f'{key}="{value}"'

        def serialize_pool_url(key: str, value: PoolUrl) -> str:
            return f'{key}="{str(value)}"'

        def serialize_bool(key: str, value: bool) -> str:
            return f"{key}={str(value).lower()}"

        serialization_map: dict[type, Callable[[str, Any], str]] = {
            int: serialize_int,
            float: serialize_float,
            str: serialize_str,
            bool: serialize_bool,
            PoolUrl: serialize_pool_url,
        }

        include = [
            "url",
            "accepted",
            "rejected",
            "active",
            "alive",
            "user",
        ]

        field_data = []
        for field in include:
            field_val = getattr(self, field)
            if field_val is None:
                continue
            serialization_func = serialization_map.get(type(field_val))
            if serialization_func is not None:
                serialized = serialization_func(
                    f"{key_root}{level_delimiter}{field}", field_val
                )
                if serialized is not None:
                    field_data.append(serialized)

        return ",".join(field_data)
