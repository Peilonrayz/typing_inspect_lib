import sys
import typing
from typing import KT, T, T_co, T_contra, VT, VT_co, V_co

try:
    from typing import CT_co
except ImportError:
    CT_co = typing.TypeVar('CT_co', bound=type, covariant=True)

try:
    from typing import CT
except ImportError:
    CT = typing.TypeVar('CT_co', bound=type, covariant=True)

CT_te = CT if sys.version_info[:3] != (3, 5, 2) else typing.TypeVar('CT', bound=type)


__all__ = [
    'CT',
    'CT_co',
    'CT_te',
    'KT',
    'T',
    'T_co',
    'T_contra',
    'VT',
    'VT_co',
    'V_co',
]
