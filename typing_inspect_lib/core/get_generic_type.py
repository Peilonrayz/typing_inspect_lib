import typing

from .helpers import PY_OLD, typing_

if PY_OLD:
    def get_generic_type(type_):
        """Gets the generic type of the type provided, and if the type is a generic unwrapped type."""
        ret_type = None
        if isinstance(type_, typing._ProtocolMeta):
            ret_type = typing_.BaseProtocol
        elif isinstance(type_, typing_.ProtocolMeta):
            ret_type = typing_.Protocol
        elif isinstance(type_, typing.GenericMeta):
            ret_type = typing.Generic

        if ret_type is not None:
            if type_.__origin__ is None:
                return ret_type, True
            else:
                return ret_type, False
        return None, None
else:
    def get_generic_type(type_):
        if isinstance(type_, typing._ProtocolMeta):
            return typing_.BaseProtocol, True
        if isinstance(type_, typing_.ProtocolMeta):
            return typing_.Protocol, True

        if isinstance(type_, typing._GenericAlias):
            if isinstance(type_.__origin__, typing._ProtocolMeta):
                return typing_.BaseProtocol, False
            elif isinstance(type_.__origin__, typing_.ProtocolMeta):
                return typing_.Protocol, False
            elif getattr(type_, '_special', False):
                return typing.Generic, True
            else:
                return typing.Generic, False
        if hasattr(type_, '__orig_bases__') and typing.Generic in type_.__mro__:
            return typing.Generic, True
        return None, None