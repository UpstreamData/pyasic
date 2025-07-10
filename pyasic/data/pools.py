from enum import Enum
from typing import Optional
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
    port: Optional[int] = None
    pubkey: Optional[str] = None

    @model_serializer
    def serialize(self):
        return str(self)

    def __str__(self) -> str:
        port_str = f":{self.port}" if self.port is not None else ""
        if self.scheme == Scheme.STRATUM_V2 and self.pubkey:
            return f"{self.scheme.value}://{self.host}{port_str}/{self.pubkey}"
        else:
            return f"{self.scheme.value}://{self.host}{port_str}"

    @classmethod
    def from_str(cls, url: str) -> Self | None:
        parsed_url = urlparse(url)
        if not parsed_url.hostname:
            return None
        # Если схема отсутствует, используем схему по умолчанию
        scheme = (
            Scheme(parsed_url.scheme)
            if parsed_url.scheme.strip() != ""
            else Scheme.STRATUM_V1
        )
        host = parsed_url.hostname
        port = parsed_url.port  # может быть None, если порт не указан
        pubkey = parsed_url.path.lstrip("/") if scheme == Scheme.STRATUM_V2 else None
        return cls(scheme=scheme, host=host, port=port, pubkey=pubkey)


class PoolMetrics(BaseModel):
    """
    A dataclass to standardize pool metrics returned from miners.
    Attributes:
        accepted: Number of accepted shares.
        rejected: Number of rejected shares.
        get_failures: Number of failures in obtaining work from the pool.
        remote_failures: Number of failures communicating with the pool server.
        active: Indicates if the miner is connected to the stratum server.
        alive: Indicates if a pool is alive.
        url: URL of the pool.
        index: Index of the pool.
        user: Username for the pool.
        pool_rejected_percent: Percentage of rejected shares by the pool.
        pool_stale_percent: Percentage of stale shares by the pool.
    """

    url: Optional[PoolUrl]
    accepted: Optional[int] = None
    rejected: Optional[int] = None
    get_failures: Optional[int] = None
    remote_failures: Optional[int] = None
    active: Optional[bool] = None
    alive: Optional[bool] = None
    index: Optional[int] = None
    user: Optional[str] = None

    @computed_field  # type: ignore[misc]
    @property
    def pool_rejected_percent(self) -> float:
        """Calculate and return the percentage of rejected shares."""
        total = (self.accepted or 0) + (self.rejected or 0)
        return self._calculate_percentage(self.rejected, total)

    @computed_field  # type: ignore[misc]
    @property
    def pool_stale_percent(self) -> float:
        """Calculate and return the percentage of stale shares."""
        total = (self.accepted or 0) + (self.rejected or 0)
        return self._calculate_percentage(self.get_failures, total)

    @staticmethod
    def _calculate_percentage(value: Optional[int], total: int) -> float:
        """Calculate the percentage."""
        if value is None or total == 0:
            return 0
        return (value / total) * 100

    def as_influxdb(self, key_root: str, level_delimiter: str = ".") -> str:

        def serialize_int(key: str, value: int) -> str:
            return f"{key}={value}"

        def serialize_float(key: str, value: float) -> str:
            return f"{key}={value}"

        def serialize_str(key: str, value: str) -> str:
            return f'{key}="{value}"'

        def serialize_pool_url(key: str, value: str) -> str:
            return f'{key}="{str(value)}"'

        def serialize_bool(key: str, value: bool):
            return f"{key}={str(value).lower()}"

        serialization_map = {
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
            serialization_func = serialization_map.get(
                type(field_val), lambda _k, _v: None
            )
            serialized = serialization_func(
                f"{key_root}{level_delimiter}{field}", field_val
            )
            if serialized is not None:
                field_data.append(serialized)

        return ",".join(field_data)
