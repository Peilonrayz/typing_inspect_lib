import typing

from typing_inspect_lib import get_type_info, get_type_var_info
from typing_inspect_lib.core.get_type_info import _TypeInfo
from typing_inspect_lib.core.helpers import compatibility
from typing_inspect_lib.core.helpers.helpers import safe_contains
from typing_inspect_lib.core.helpers.links import LITERAL_TYPES

__all__ = [
    'Type',
    'VarType',
    'build_types',
]

Type = _TypeInfo
VarType = get_type_var_info


def build_types(type_):
    type_info = get_type_info(type_)
    if type_info is None:
        return None

    if type_info.unwrapped is typing.TypeVar:
        return VarType(type_info.origin)

    if safe_contains(LITERAL_TYPES, type_info.unwrapped):
        return type_info.unwrapped

    if type_info.unwrapped is compatibility.typings.NewType:
        return type_info.origin

    return Type(
        type_info.unwrapped,
        type_info.origin,
        type_,
        tuple(build_types(a) for a in type_info.args),
        tuple(build_types(p) for p in type_info.parameters),
    )
