"""Interface to :mod:`typing`."""

# pylint: disable=invalid-name

import sys
import typing
try:
    import typing_extensions
except ImportError:
    _HAS_TE = False
else:
    _HAS_TE = True

from .helpers import gen_type as _gen_type

_VERSION = sys.version_info[:3]
_PY35 = _VERSION[:2] == (3, 5)
_PY36 = _VERSION[:2] == (3, 6)

__all__ = [
    'BaseProtocol',
    'ClassVar',
    '_ClassVar',
    'ClassVarMeta',
    'NewType',
    'Protocol',
    'ProtocolMeta',
    '_Union',
]


if _HAS_TE:
    NewType = typing_extensions.NewType
else:
    NewType = _gen_type('NewType')()

BaseProtocol = _gen_type('BaseProtocol')()

if _VERSION == (3, 5, 0) or not _HAS_TE:
    Protocol = _gen_type('Protocol')()
    ProtocolMeta = _gen_type('ProtocolMeta')
else:
    Protocol = typing_extensions.Protocol
    ProtocolMeta = getattr(
        typing_extensions,
        '_ProtocolMeta',
        _gen_type('ProtocolMeta'),
    )

if _PY35 and _VERSION <= (3, 5, 2):
    if _HAS_TE:
        ClassVar = typing_extensions.ClassVar
        ClassVarMeta = typing_extensions._ClassVarMeta
    else:
        ClassVar = _gen_type('ClassVar')()
        ClassVarMeta = _gen_type('ClassVarMeta')
else:
    ClassVar = typing.ClassVar
    ClassVarMeta = _gen_type('ClassVarMeta')

if _PY35 and _VERSION <= (3, 5, 2):
    if _HAS_TE:
        _ClassVar = typing_extensions.ClassVar
    else:
        _ClassVar = _gen_type('_ClassVar')()
    _Union = typing.Union
elif _VERSION < (3, 7, 0):
    _ClassVar = typing._ClassVar
    _Union = typing._Union
else:
    _ClassVar = typing.ClassVar
    _Union = typing.Union
