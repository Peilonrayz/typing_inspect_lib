import typing

from typing_inspect_lib import get_type_info, get_type_var_info
from typing_inspect_lib.core.helpers import LITERAL_TYPES, safe_dict_contains
from typing_inspect_lib.core.get_type_info import _TypeInfo
from typing_inspect_lib.core.helpers import typing_

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

    if type_info.typing is typing.TypeVar:
        return VarType(type_info.class_)

    if safe_dict_contains(LITERAL_TYPES, type_info.typing):
        return type_info.typing

    if type_info.typing is typing_.NewType:
        return type_info.class_

    return Type(
        type_info.typing,
        type_info.class_,
        tuple(build_types(a) for a in type_info.args),
        tuple(build_types(p) for p in type_info.parameters),
    )
