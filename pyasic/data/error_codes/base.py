from pydantic import BaseModel


class BaseMinerError(BaseModel):
    error_code: int | None = None

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

    def as_influxdb(self, root_key: str, level_delimiter: str = ".") -> str:
        field_data = []

        if self.error_code is not None:
            field_data.append(
                f"{root_key}{level_delimiter}error_code={self.error_code}"
            )

        # Check if error_message exists as an attribute (either regular or computed field)
        if hasattr(self, "error_message"):
            error_message = getattr(self, "error_message")
            if error_message is not None:
                field_data.append(
                    f'{root_key}{level_delimiter}error_message="{error_message}"'
                )

        return ",".join(field_data)
