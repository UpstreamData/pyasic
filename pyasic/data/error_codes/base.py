from pydantic import BaseModel


class BaseMinerError(BaseModel):
    @classmethod
    def fields(cls):
        return list(cls.model_fields.keys())

    def asdict(self) -> dict:
        return self.model_dump()

    def as_dict(self) -> dict:
        """Get this dataclass as a dictionary.

        Returns:
            A dictionary version of this class.
        """
        return self.asdict()
