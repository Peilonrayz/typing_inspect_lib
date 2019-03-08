from .get import get_args, get_generic_type, get_parameters, get_special_type, get_type_var_info, get_typing
from .types_ import Type, VarType, LiteralType, NewType, build_types

from ._compat.typing_ import BaseProtocol as BaseProtocol_, ClassVar as ClassVar_, NewType as NewType_, NoReturn as NoReturn_, Protocol as Protocol_, Type as Type_

__all__ = [
    'LiteralType',
    'NewType',
    'Type',
    'VarType',
    'build_types',
    'get_args',
    # 'get_generic_type',
    'get_parameters',
    'get_special_type',
    'get_type_var_info',
    'get_typing',

    # Types returned by `get_special_type` for compatibility
    'ClassVar_',
    'NewType_',
    'NoReturn_',
    'Protocol_',
    'Type_',

    # Types returned by `get_generic_type` for compatibility
    # 'Protocol_',
    # 'BaseProtocol_',
]
