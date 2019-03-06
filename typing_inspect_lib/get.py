import collections
import sys
import types
import typing

from ._compat import typing_, abc

__all__ = [
    'get_args',
    'get_generic_type',
    'get_parameters',
    'get_special_type',
    'get_typing',
]

_VERSION = sys.version_info[:3]
_PY35 = _VERSION[:2] == (3, 5)
_PY350_2 = (3, 5, 0) <= _VERSION <= (3, 5, 2)
_PY_OLD = _VERSION < (3, 7, 0)

# Non-generic literal types that should be returned by `get_class` and `get_typing`
_TYPING_LITERAL = {
    typing.Hashable,
    typing.Sized
}

# Types used to get the special type.
_SPECIAL_TYPES = {
    typing.Callable: typing.Callable,
    typing_._ClassVar: typing_.ClassVar,
    typing.Generic: typing.Generic,
    typing.NamedTuple: typing.NamedTuple,
    typing.Optional: typing.Optional,
    typing.Tuple: typing.Tuple,
    typing_._Union: typing.Union,
    typing_.Type: typing_.Type
}

if _VERSION != (3, 5, 0):
    _SPECIAL_TYPES[typing_.Protocol] = typing_.Protocol

_WRAPPED_SPECIAL_TYPES = {
    (typing.CallableMeta if _PY_OLD else collections.abc.Callable): typing.Callable,
    (typing_.ClassVarMeta if _PY350_2 else typing_._ClassVar): typing_.ClassVar,
    # (GenericMeta if PY350_2 else Generic): Generic,
    typing.Generic: typing.Generic,
    (typing.OptionalMeta if _PY350_2 else typing.Optional): typing.Optional,
    (typing.TupleMeta if _PY_OLD else tuple): typing.Tuple,
    (typing.UnionMeta if _PY350_2 else typing_._Union): typing.Union,
}

if _VERSION >= (3, 7, 0):
    _WRAPPED_SPECIAL_TYPES[type] = typing.Type


def _get_special_uni(type_):
    if isinstance(type_, typing.TypeVar):
        return typing.TypeVar
    if isinstance(type_, typing_.ProtocolMeta):
        return typing_.Protocol
    if isinstance(type_, types.FunctionType) and hasattr(type_, '__supertype__'):
        return typing_.NewType
    return None


if _PY_OLD:
    def get_special_type(type_):
        try:
            base_type = _SPECIAL_TYPES.get(type_)
        except TypeError:
            pass
        else:
            if base_type is not None:
                return base_type
        t = type(type_)
        try:
            unwrapped = _WRAPPED_SPECIAL_TYPES.get(t)
        except TypeError:
            pass
        else:
            if unwrapped is not None:
                return unwrapped
        if t is typing.GenericMeta:
            # To allow <type>[T] to return correctly
            if getattr(type_, '__origin__', None) is typing.Generic:
                return typing.Generic
            if getattr(type_, '__origin__', None) is typing_.Type:
                return typing_.Type
        return _get_special_uni(type_)
else:
    def get_special_type(type_):
        try:
            base_type = _SPECIAL_TYPES.get(type_)
        except TypeError:
            pass
        else:
            if base_type is not None:
                return base_type
        if isinstance(type_, typing._GenericAlias):
            try:
                unwrapped = _WRAPPED_SPECIAL_TYPES.get(type_.__origin__)
            except TypeError:
                pass
            else:
                if unwrapped is not None:
                    return unwrapped
        return _get_special_uni(type_)


if _PY_OLD:
    def get_generic_type(type_):
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
        return None, False
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
        return None, False


def _is_builtin(type_):
    module = getattr(type_, '__module__', None)
    name = getattr(type_, '__name__', None)
    if module is None or name is None:
        return None
    if module in {'typing', 'typing_extensions'}:
        return True
    return False


if _PY_OLD:
    def _get_wrapped_typing(type_):
        gorg = getattr(type_, '_gorg', None)
        if gorg is not None:
            return gorg
        return _get_origins(type_)[-1]
else:
    _CONV_NAMES = {
        'AbstractAsyncContextManager': 'AsyncContextManager',
        'AbstractContextManager': 'ContextManager'
    }

    def _get_wrapped_typing(type_):
        name = type_._name
        if name is None:
            return getattr(type_, '__origin__', None)
        return getattr(typing, _CONV_NAMES.get(name, name), None)


if _PY_OLD:
    def _get_other_typing(type_):
        if type_ in _TYPING_LITERAL:
            return type_
        return None
else:
    def _get_other_typing(type_):
        return None


if _PY_OLD:
    _CLASS_LOC = '__extra__'
else:
    _CLASS_LOC = '__origin__'


if _PY35 and _VERSION <= (3, 5, 0):
    def _get_generic_class(type_):
        if _is_builtin(type_):
            return getattr(type_, _CLASS_LOC, None)
        return None
else:
    def _get_generic_class(type_):
        return getattr(type_, _CLASS_LOC, None)


def _is_type_alias(type_):
    return type(type_) is typing._TypeAlias


def _get_origins(type_):
    origins = [type_]
    if hasattr(type_, '__origin__'):
        while type_.__origin__ is not None:
            type_ = type_.__origin__
            origins.append(type_)
    return origins


_CLASS_TYPES = {
    typing.Callable: abc.Callable,
    typing.Tuple: tuple,
    typing_.Type: type,
}


def _convert_special_type(type_):
    return _CLASS_TYPES.get(type_, type_)


def _get_typing(type_):
    special_type = get_special_type(type_)
    if special_type is not None:
        return special_type, _convert_special_type(special_type)

    generic_type, base = get_generic_type(type_)
    if generic_type is not None:
        if base:
            return type_, _get_generic_class(type_)
        return _get_wrapped_typing(type_), _get_generic_class(type_)
    return _get_other_typing(type_), None


def get_typing(type_):
    t, c = _get_typing(type_)
    if t is None:
        t = c
    if c is None:
        c = t
    return t, c


def _parameters_link(args, parameters):
    args_ = {}
    for i, a in enumerate(args):
        args_.setdefault(a, []).append(i)
    args_ = {k: iter(v) for k, v in args_.items()}
    return [next(args_.get(p, iter([p]))) for p in parameters]


if _PY35 and _VERSION <= (3, 5, 2):
    def _handle_special_type(type_):
        special_type = get_special_type(type_)
        if special_type is not None:
            if special_type is typing_.ClassVar:
                return (type_.__type__,) if type_.__type__ is not None else ()
            if special_type is typing.Callable:
                args = type_.__args__
                ret = type_.__result__
                if args is None and ret is None:
                    return ()
                return tuple(args) + (ret,)
            if special_type is typing.Generic:
                return type_.__parameters__ or ()
            if special_type is typing.Union:
                return type_.__union_params__ or ()
            if special_type is typing.Tuple:
                return type_.__tuple_params__ or ()
        return None
elif _PY_OLD:
    def _handle_special_type(type_):
        if get_special_type(type_) is typing.ClassVar:
            return (type_.__type__,) if type_.__type__ is not None else ()
        return None


if _PY35 and _VERSION <= (3, 5, 1):
    def _handle_origin(type_):
        if getattr(type_, '__origin__', None) is not None:
            return getattr(type_, '__parameters__', None) or ()
        return None
elif _PY_OLD:
    def _handle_origin(type_):
        origins = _get_origins(type_)
        origin, origins = origins[0], origins[1:]
        args = list(getattr(origin, '__args__', None) or [])
        for origin_ in origins:
            links = _parameters_link(args, origin.__parameters__)
            origin = origin_
            for link, arg in zip(links, getattr(origin, '__args__', None) or []):
                args[link] = arg
        return tuple(args)


if _PY_OLD:
    def get_args(type_):
        if _is_type_alias(type_):
            return type_.type_var,
        _, base = get_generic_type(type_)
        if base:
            return ()
        special_args = _handle_special_type(type_)
        if special_args is not None:
            return special_args
        origin_args = _handle_origin(type_)
        if origin_args is not None:
            return origin_args
        return ()
else:
    def get_args(type_):
        _, base = get_generic_type(type_)
        if base:
            return ()
        return getattr(type_, '__args__', None) or ()


def _args_to_parameters(args):
    return tuple(a for a in args if get_special_type(a) is typing.TypeVar)


def get_parameters(type_):
    parameters = getattr(type_, '__parameters__', None)
    return parameters if parameters is not None else ()
