import typing

from typing_inspect_lib.core.helpers import LITERAL_TYPES, typing_, safe_dict_contains
from typing_inspect_lib import get_type_info, get_type_var_info
from typing_inspect_lib.core.get_type_info import _TypeInfo

__all__ = [
    'Type',
    'VarType',
    'build_types',
]

Type = _TypeInfo
VarType = get_type_var_info


def build_types(type_):
    t = get_type_info(type_)
    if t is None:
        return None

    if t.typing is typing.TypeVar:
        return VarType(t.class_)

    if safe_dict_contains(LITERAL_TYPES, t.typing):
        return t.typing

    if t.typing is typing_.NewType:
        return t.class_

    return Type(
        t.typing,
        t.class_,
        tuple(build_types(a) for a in t.args),
        tuple(build_types(p) for p in t.parameters)
    )
