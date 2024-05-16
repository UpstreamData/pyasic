from dataclasses import dataclass


@dataclass
class PoolMetrics:
    """A dataclass to standardize pool metrics returned from miners.
    Attributes:

    accepted: Number of accepted shares.
    rejected: Number of rejected shares.
    get_failures: Number of failures in obtaining work from the pool.
    remote_failures: Number of failures communicating with the pool server.
    stratum_active: Indicates if the miner is connected to the stratum server.
    pool_rejected_percent: Percentage of rejected shares by the pool.
    pool_stale_percent: Percentage of stale shares by the pool.
    """

    accepted: int
    rejected: int
    get_failures: int
    remove_failures: int
    stratum_active: bool

    @property
    def pool_rejected_percent(self) -> float:
        """Calculate and return the percentage of rejected shares"""
        return self._calculate_percentage(self.rejected, self.accepted + self.rejected)

    @property
    def pool_stale_percent(self) -> float:
        """Calculate and return the percentage of stale shares."""
        return self._calculate_percentage(
            self.get_failures, self.accepted + self.rejected
        )

    @staticmethod
    def _calculate_percentage(value: int, total: int) -> float:
        """Calculate the percentage."""
        if total == 0:
            return 0
        return (value / total) * 100
