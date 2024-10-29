from datetime import datetime, timedelta
from typing import Any, Dict

from betterproto import DATETIME_ZERO, TYPE_MAP, TYPE_MESSAGE, Casing, Message


# https://github.com/danielgtaylor/python-betterproto/pull/609
def to_pydict(
    self, casing: Casing = Casing.CAMEL, include_default_values: bool = False
) -> Dict[str, Any]:
    """
    Returns a python dict representation of this object.

    Parameters
    -----------
    casing: :class:`Casing`
        The casing to use for key values. Default is :attr:`Casing.CAMEL` for
        compatibility purposes.
    include_default_values: :class:`bool`
        If ``True`` will include the default values of fields. Default is ``False``.
        E.g. an ``int32`` field will be included with a value of ``0`` if this is
        set to ``True``, otherwise this would be ignored.

    Returns
    --------
    Dict[:class:`str`, Any]
        The python dict representation of this object.
    """
    output: Dict[str, Any] = {}
    defaults = self._betterproto.default_gen
    for field_name, meta in self._betterproto.meta_by_field_name.items():
        field_is_repeated = defaults[field_name] is list
        try:
            value = getattr(self, field_name)
        except AttributeError:
            value = self._get_field_default(field_name)
        cased_name = casing(field_name).rstrip("_")  # type: ignore
        if meta.proto_type == TYPE_MESSAGE:
            if isinstance(value, datetime):
                if (
                    value != DATETIME_ZERO
                    or include_default_values
                    or self._include_default_value_for_oneof(
                        field_name=field_name, meta=meta
                    )
                ):
                    output[cased_name] = value
            elif isinstance(value, timedelta):
                if (
                    value != timedelta(0)
                    or include_default_values
                    or self._include_default_value_for_oneof(
                        field_name=field_name, meta=meta
                    )
                ):
                    output[cased_name] = value
            elif meta.wraps:
                if value is not None or include_default_values:
                    output[cased_name] = value
            elif field_is_repeated:
                # Convert each item.
                value = [i.to_pydict(casing, include_default_values) for i in value]
                if value or include_default_values:
                    output[cased_name] = value
            elif value is None:
                if include_default_values:
                    output[cased_name] = None
            elif (
                value._serialized_on_wire
                or include_default_values
                or self._include_default_value_for_oneof(
                    field_name=field_name, meta=meta
                )
            ):
                output[cased_name] = value.to_pydict(casing, include_default_values)
        elif meta.proto_type == TYPE_MAP:
            for k in value:
                if hasattr(value[k], "to_pydict"):
                    value[k] = value[k].to_pydict(casing, include_default_values)

            if value or include_default_values:
                output[cased_name] = value
        elif (
            value != self._get_field_default(field_name)
            or include_default_values
            or self._include_default_value_for_oneof(field_name=field_name, meta=meta)
        ):
            output[cased_name] = value
    return output


def patch():
    Message.to_pydict = to_pydict
