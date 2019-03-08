import sys
import typing

from . import get
from ._compat import typing_

__all__ = [
    'LiteralType',
    'NewType',
    'Type',
    'VarType',
    'build_types',
]

_VERSION = sys.version_info[:3]

_SPECIAL_TYPES = {
    typing_.ClassVar
}


class Type:
    def __init__(self, typing_, class_, args, parameters=None):
        self.typing = typing_
        self.class_ = class_
        self.args = tuple(args)
        self.parameters = tuple(parameters) if parameters else ()

    def __eq__(self, other):
        if not isinstance(other, Type):
            return False
        if self.typing in _SPECIAL_TYPES:
            if self.typing is not other.typing:
                return False
            if self.class_ is not other.class_:
                return False
        else:
            if self.typing != other.typing:
                return False
            if self.class_ != other.class_:
                return False
        return self.args == other.args and self.parameters == other.parameters

    def __repr__(self):
        return 'Type({self.typing}, {self.class_}, args={args}, parameters={parameters})'.format(self=self, args=self.args, parameters=self.parameters)

    def __str__(self):
        args = ''
        if any(a.typing is not typing.Any for a in self.args):
            args = ', '.join(repr(a) for a in self.args)
            if args:
                args = '[{args}]'.format(args=args)
        return 'Type<{self.typing}{args}>'.format(self=self, args=args)


class VarType:
    def __init__(self, type_):
        self.typing = type_
        tv = get.get_type_var_info(type_)
        self.name = tv.name
        self.bound = tv.bound
        self.covariant = tv.covariant
        self.contravariant = tv.contravariant

    def __eq__(self, other):
        if not isinstance(other, VarType):
            return False
        return all([
            self.name == other.name,
            self.bound == other.bound,
            self.covariant == other.covariant,
            self.contravariant == other.contravariant
        ])

    def __repr__(self):
        return 'VT<{}>'.format(self.typing)
        # return 'VT<{} {} {} {}>'.format(self.name, self.bound, self.covariant, self.contravariant)


_LITERALS = {
    typing.Any,
    str,
    type(None),
    bytes,
    int,
    typing_.NoReturn
}

if _VERSION < (3, 0, 0):
    _LITERALS.add(unicode)


class LiteralType:
    def __init__(self, type_):
        self.typing = type_

    def __eq__(self, other):
        return all([
            isinstance(other, LiteralType),
            self.typing == other.typing,
        ])

    def __repr__(self):
        return 'LT<{self.typing}>'.format(self=self)


class NewType:
    def __init__(self, type_):
        self.typing = type_

    def __eq__(self, other):
        return all([
            isinstance(other, NewType),
            self.typing == other.typing,
        ])

    def __repr__(self):
        return '{self.typing}'.format(self=self)


def build_types(type_):
    special_type = get.get_special_type(type_)
    if special_type is typing_.NewType:
        return NewType(type_)
    if type_ in _LITERALS:
        return LiteralType(type_)
    if special_type is typing.TypeVar:
        return VarType(type_)
    t_typing, class_ = get.get_typing(type_)
    args = tuple(build_types(a) for a in get.get_args(type_))
    parameters = tuple(build_types(p) for p in get.get_parameters(type_))
    return Type(t_typing, class_, args, parameters)
