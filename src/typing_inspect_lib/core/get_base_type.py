"""Get base types."""

import typing

from .helpers import compatibility, helpers

# TODO: reduce complexity
if helpers.PY_OLD:  # noqa: MC0001
    def get_base_type(type_):  # pylint: disable=too-many-return-statements
        ret_type = None
        if isinstance(type_, typing._ProtocolMeta):
            ret_type = compatibility.typing.Protocol
        elif isinstance(type_, compatibility.typing_extensions._ProtocolMeta):
            ret_type = compatibility.typing_extensions.Protocol
        elif isinstance(type_, typing.GenericMeta):
            ret_type = typing.Generic

        if ret_type is not None:
            if type_.__origin__ is None:
                return ret_type, True
            else:
                return ret_type, False
        return None, None
else:
    def get_base_type(type_):  # pylint: disable=too-many-return-statements
        if isinstance(type_, typing._ProtocolMeta):
            return compatibility.typing.Protocol, True
        if isinstance(type_, compatibility.typing_extensions._ProtocolMeta):
            return compatibility.typing_extensions.Protocol, True

        if isinstance(type_, typing._GenericAlias):
            if isinstance(type_.__origin__, typing._ProtocolMeta):
                return compatibility.typing.BaseProtocol, False
            elif isinstance(type_.__origin__, compatibility.typing_extensions._ProtocolMeta):
                return compatibility.typing_extensions.Protocol, False
            elif getattr(type_, '_special', False):
                return typing.Generic, True
            else:
                return typing.Generic, False
        if hasattr(type_, '__orig_bases__') and typing.Generic in type_.__mro__:
            return typing.Generic, True
        return None, None
get_base_type.__doc__ = """Get the generic type and if it is unwrapped."""
