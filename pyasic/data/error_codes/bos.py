from dataclasses import dataclass, asdict


@dataclass
class BraiinsOSError:
    """A Dataclass to handle error codes of BraiinsOS+ miners."""

    error_message: str

    def asdict(self):
        return asdict(self)
