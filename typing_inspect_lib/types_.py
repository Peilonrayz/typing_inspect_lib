import sys
import typing

from .links import LITERAL_TYPES
from . import get
from ._compat import typing_
from .helpers import _safe_dict_contains

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


class BaseType(object):
    # typing: typing.Any
    pass


class Type(BaseType):
    def __init__(self, typing_, class_, args, parameters):
        self.typing = typing_
        self.class_ = class_
        self.args = tuple(args)
        self.parameters = tuple(parameters)

    def __hash__(self):
        return hash(sum(hash(i) for i in (self.typing, self.class_, self.args, self.parameters)))

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
        # return 'Type<{self.typing}[{self.args}]>'.format(self=self)
        return 'Type({self.typing}, {self.class_}, args={self.args}, parameters={self.parameters})'.format(self=self)

    def __str__(self):
        args = ''
        if any(a.typing is not typing.Any for a in self.args):
            args = ', '.join(repr(a) for a in self.args)
            if args:
                args = '[{args}]'.format(args=args)
        return 'Type<{self.typing}{args}>'.format(self=self, args=args)

    def __getitem__(self, item):
        if not isinstance(item, tuple):
            item = item,

        return type(self)(self.typing, self.class_, self.args + item, self.parameters[len(item):])


class VarType(BaseType):
    def __init__(self, type_):
        self.type = type_
        self.typing = typing.TypeVar
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
        return 'VT<{}>'.format(self.type)
        # return 'VT<{} {} {} {}>'.format(self.name, self.bound, self.covariant, self.contravariant)


class LiteralType(BaseType):
    def __init__(self, type_):
        self.typing = type_

    def __eq__(self, other):
        if not isinstance(other, LiteralType):
            return False
        return self.typing == other.typing

    def __repr__(self):
        return 'LT<{self.typing}>'.format(self=self)

    def __hash__(self):
        return hash(self.typing)


class NewType(BaseType):
    def __init__(self, type_):
        self.typing = type_

    def __eq__(self, other):
        if not isinstance(other, NewType):
            return False
        return self.typing == other.typing

    def __repr__(self):
        return '{self.typing}'.format(self=self)


def build_types_info(t):
    if t is None:
        return None

    if t.typing is typing.TypeVar:
        return VarType(t.class_)

    if _safe_dict_contains(LITERAL_TYPES, t.typing):
        return LiteralType(t.typing)

    if t.typing is typing_.NewType:
        return NewType(t.class_)

    return Type(
        t.typing,
        t.class_,
        tuple(build_types(a) for a in t.args),
        tuple(build_types(p) for p in t.parameters)
    )


def build_types(type_):
    t = get.get_type_info(type_)
    return build_types_info(t)
