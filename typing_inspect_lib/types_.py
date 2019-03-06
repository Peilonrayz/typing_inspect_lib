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


class Type:
    def __init__(self, typing_, class_, args=None):
        if args is None:
            try:
                parameters = len(typing_.__parameters__)
            except (AttributeError, TypeError):
                parameters = 0
            args = tuple([LiteralType(typing.Any)] * parameters)
        self.typing = typing_
        self.class_ = class_
        self.args = tuple(args)
        self._parameters = get._args_to_parameters(args)

    def __eq__(self, other):
        if not isinstance(other, Type):
            return False
        if not (self.typing is other.typing):
            return False
        return all([
            self.class_ == other.class_,
            self.args == other.args
        ])

    def __repr__(self):
        args = None if all(t.typing is typing.Any for t in self.args) else self.args
        return 'Type({self.typing}, {self.class_}, args={args})'.format(self=self, args=args)

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

    def __eq__(self, other):
        return all([
            isinstance(other, VarType),
            self.typing == other.typing
        ])

    def __repr__(self):
        return str(self.typing)


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
    if not args:
        args = None
    return Type(t_typing, class_, args)
