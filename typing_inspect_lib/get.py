import typing
import types
import collections
import itertools
try:
    import typing_extensions
except ImportError:
    pass

from .links import VERSION, PY_35, PY_OLD
from ._compat import typing_, abc


__all__ = [
    'get_args',
    'get_bases',
    'get_generic_type',
    'get_parameters',
    'get_special_type',
    'get_type_info',
    'get_type_var_info',
    'get_typing',
    'get_mro',
    'get_mro_orig'
]

# Origin code


def _get_origins(type_):
    origins = [type_]
    if hasattr(type_, '__origin__'):
        while getattr(type_, '__origin__', None) is not None:
            type_ = type_.__origin__
            origins.append(type_)
    return origins


# Get typing code

_PY350_2 = (3, 5, 0) <= VERSION <= (3, 5, 2)

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

if VERSION != (3, 5, 0):
    _SPECIAL_TYPES[typing_.Protocol] = typing_.Protocol

_WRAPPED_SPECIAL_TYPES = {
    (typing.CallableMeta if PY_OLD else collections.abc.Callable): typing.Callable,
    (typing_.ClassVarMeta if _PY350_2 else typing_._ClassVar): typing_.ClassVar,
    # (GenericMeta if PY350_2 else Generic): Generic,
    typing.Generic: typing.Generic,
    (typing.OptionalMeta if _PY350_2 else typing.Optional): typing.Optional,
    (typing.TupleMeta if PY_OLD else tuple): typing.Tuple,
    (typing.UnionMeta if _PY350_2 else typing_._Union): typing.Union,
}

if VERSION >= (3, 7, 0):
    _WRAPPED_SPECIAL_TYPES[type] = typing.Type

_LITERALS = {
    typing.Any,
    str,
    type(None),
    bytes,
    int,
    typing_.NoReturn
}

if VERSION < (3, 0, 0):
    _LITERALS.add(unicode)


def _args_to_parameters(args):
    return tuple(a for a in args if get_special_type(a) is typing.TypeVar)


def _get_safe(dict_, key, default=None):
    try:
        return dict_.get(key, default)
    except TypeError:
        return default


def _get_special_uni(type_):
    if isinstance(type_, typing.TypeVar):
        return typing.TypeVar
    if isinstance(type_, typing_.ProtocolMeta):
        return typing_.Protocol
    if isinstance(type_, types.FunctionType) and hasattr(type_, '__supertype__'):
        return typing_.NewType
    return None


if PY_OLD:
    def get_special_type(type_):
        base_type = _get_safe(_SPECIAL_TYPES, type_)
        if base_type is not None:
            return base_type
        t = type(type_)
        unwrapped = _get_safe(_WRAPPED_SPECIAL_TYPES, t)
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
        base_type = _get_safe(_SPECIAL_TYPES, type_)
        if base_type is not None:
            return base_type
        if isinstance(type_, typing._GenericAlias):
            unwrapped = _get_safe(_WRAPPED_SPECIAL_TYPES, type_.__origin__)
            if unwrapped is not None:
                return unwrapped
        return _get_special_uni(type_)


if PY_OLD:
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


if PY_OLD:
    def _get_other_typing(type_):
        try:
            if type_ in _TYPING_LITERAL:
                return type_
        except TypeError:
            pass
        return None
else:
    def _get_other_typing(type_):
        return None


if PY_OLD:
    _CLASS_LOC = '__extra__'
else:
    _CLASS_LOC = '__origin__'


def _is_builtin(type_):
    module = getattr(type_, '__module__', None)
    name = getattr(type_, '__name__', None)
    if module is None or name is None:
        return None
    if module in {'typing', 'typing_extensions'}:
        t = getattr(globals()[module], name, None)
        if t is not None:
            return t == type_
    return False


_OLD_CLASS = {
    (typing.Dict, abc.MutableMapping): dict,
    (typing.List, abc.MutableSequence): list,
    (typing.Set, abc.MutableSet): set,
    (typing.FrozenSet, abc.Set): frozenset
}


if PY_35 and VERSION <= (3, 5, 1):
    def _get_generic_class(type_, typing_):
        if _is_builtin(typing_):
            t = getattr(type_, _CLASS_LOC, None)
            return _OLD_CLASS.get((typing_, t), t)
        return None
else:
    def _get_generic_class(type_, typing_):
        return getattr(type_, _CLASS_LOC, None)


_CLASS_TYPES = {
    typing.Callable: abc.Callable,
    typing.Tuple: tuple,
    typing_.Type: type,
}


def _convert_special_type(special_type, type_):
    if special_type is typing_.Protocol:
        return type_
    return _CLASS_TYPES.get(special_type, special_type)


def _get_typing(type_):
    special_type = get_special_type(type_)
    if special_type is not None:
        return special_type, _convert_special_type(special_type, type_)

    generic_type, base = get_generic_type(type_)
    if generic_type is not None:
        typing_ = type_
        if not base:
            typing_ = _get_wrapped_typing(type_)
        return typing_, _get_generic_class(type_, typing_)
    return _get_other_typing(type_), None


def get_typing(type_):
    if isinstance(type_, typing.TypeVar):
        return typing.TypeVar, type_

    try:
        is_literal = type_ in _LITERALS
    except TypeError:
        pass
    else:
        if is_literal:
            return type_, type_

    t, c = _get_typing(type_)
    if t is None:
        t = c
    if c is None:
        c = t
    if t is typing_.NewType:
        c = type_
    return t, c


# Get generic type code


if PY_OLD:
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


# Get args code

def _is_type_alias(type_):
    return type(type_) is typing._TypeAlias


if PY_35 and VERSION <= (3, 5, 2):
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
elif PY_OLD:
    def _handle_special_type(type_):
        if get_special_type(type_) is typing.ClassVar:
            return (type_.__type__,) if type_.__type__ is not None else ()
        return None


def _safe_getattr_tuple(type_, key):
    try:
        return tuple(getattr(type_, key, None) or [])
    except TypeError:
        return ()


def _parameters_link(args, parameters):
    args_ = {}
    for i, a in enumerate(args):
        args_.setdefault(a, []).append(i)
    args_ = {k: iter(v) for k, v in args_.items()}
    return [next(args_.get(p, iter([p]))) for p in parameters]


if PY_35 and VERSION <= (3, 5, 1):
    def _handle_origin(type_):
        if getattr(type_, '__origin__', None) is not None:
            return _safe_getattr_tuple(type_, '__parameters__')
        return None
elif PY_OLD:
    def _handle_origin(type_):
        origins = _get_origins(type_)
        origin, origins = origins[0], origins[1:]
        args = list(_safe_getattr_tuple(origin, '__args__'))
        for origin_ in origins:
            links = _parameters_link(args, _safe_getattr_tuple(origin, '__parameters__'))
            origin = origin_
            for link, arg in zip(links, _safe_getattr_tuple(origin, '__args__')):
                args[link] = arg
        return tuple(args)


if PY_OLD:
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


# Get parameters code


if PY_35 and VERSION < (3, 5, 2):
    _USE_ARGS = {
        typing_.ClassVar,
        typing.Callable,
        typing.Union,
        typing.Tuple
    }

    def get_parameters(type_):
        if get_special_type(type_) in _USE_ARGS:
            parameters = get_args(type_)
        else:
            parameters = getattr(type_, '__parameters__', None) or ()
        return tuple(p for p in parameters if isinstance(p, typing.TypeVar))
elif PY_OLD:
    def get_parameters(type_):
        if get_special_type(type_) is typing_.ClassVar:
            return get_args(type_)
        return _safe_getattr_tuple(type_, '__parameters__')
else:
    def get_parameters(type_):
        return _safe_getattr_tuple(type_, '__parameters__')


# Type info code


_TypeInfo = collections.namedtuple('TypeInfo', ['typing', 'class_', 'args', 'parameters'])


def get_type_info(type_):
    t_typing, class_ = get_typing(type_)
    if t_typing is None and class_ is None:
        return None
    args = tuple(a for a in get_args(type_))
    parameters = tuple(p for p in get_parameters(type_))
    return _TypeInfo(t_typing, class_, args, parameters)


# TypeVar info code


_TypeVarInfo = collections.namedtuple('TypeVarInfo', ['name', 'bound', 'covariant', 'contravariant'])


def get_type_var_info(tv):
    if not isinstance(tv, typing.TypeVar):
        raise TypeError('get_type_var_info must be passed a TypeVar')
    return _TypeVarInfo(
        getattr(tv, '__name__', None),
        getattr(tv, '__bound__', None),
        getattr(tv, '__covariant__', None),
        getattr(tv, '__contravariant__', None)
    )

# MRO code


def pairwise(it):
    a, b = itertools.tee(it)
    next(b, None)
    return zip(a, b)


def _builtin_objects():
    builtins = [typing]
    try:
        typing_extensions
    except NameError:
        pass
    else:
        builtins.append(typing_extensions)

    for builtin in builtins:
        for k, v in builtin.__dict__.items():
            yield k, v


_BuiltinTypeLinks = collections.namedtuple('BuiltinTypeLinks', ['typing', 'class_'])


def _build_builtin_links():
    types = []
    for key, obj in _builtin_objects():
        t = get_type_info(obj)
        if t is not None:
            types.append(t)

    return _BuiltinTypeLinks(
        {t.typing: t for t in types},
        {t.class_: t for t in types},
    )


_BUILTIN_LINKS = _build_builtin_links()

_FROM_TYPING = {k: v.class_ for k, v in _BUILTIN_LINKS.typing.items()}
_FROM_CLASS = {k: v.typing for k, v in _BUILTIN_LINKS.class_.items()}


def _build_builtin_graph(builtins):
    graph = {k: v for k, v in builtins.class_.items()}
    for key, type_ in graph.items():
        bases = _get_bases_default(type_.class_)
        g_bases = tuple(graph.get(t, t) for _, t in bases)
        setattr(type_, '__bases', g_bases)
    return graph


def _get_mro_conv_dedupe(mro):
    collection_mro = iter(
        _FROM_TYPING.get(obj, obj)
        for obj in reversed(mro)
    )
    mro = ()
    mro_set = set()
    for obj in collection_mro:
        if obj not in mro_set:
            mro_set.add(obj)
            mro += obj,
    return tuple(reversed(mro))


def _from_types(types, index=1):
    mro = ()
    for type_ in types:
        t = get_typing(type_)[index]
        mro += type_ if t is None else t,
    return mro


if PY_35 and VERSION <= (3, 5, 0):
    def _get_mro(type_):
        return _get_mro_conv_dedupe(_from_types(_safe_getattr_tuple(type_, '__mro__')))
elif PY_OLD:
    def _get_mro(type_):
        return _get_mro_conv_dedupe(_safe_getattr_tuple(type_, '__mro__'))
else:
    def _get_mro(type_):
        return _safe_getattr_tuple(type_, '__mro__')


def get_mro(type_):
    type_ = _FROM_TYPING.get(type_, type_)
    if type_ not in _BUILTIN_LINKS.class_:
        _, type_ = get_typing(type_)
    return _get_mro(type_)


_BaseObj = collections.namedtuple('BaseObj', ['typing', 'class_', 'orig'])


def _get_bases_typing(type_):
    typings = _safe_getattr_tuple(type_, '__bases__')
    if not typings:
        return None
    return tuple(
        (
            typing_,
            _FROM_TYPING.get(typing_, typing_),
        )
        for typing_ in typings
    )


def _get_bases_class(type_):
    classes = _safe_getattr_tuple(type_, '__bases__')
    if not classes:
        return None
    return tuple(
        (
            _FROM_CLASS.get(class_, class_),
            class_,
        )
        for class_ in classes
    )


if PY_35 and VERSION <= (3, 5, 0):
    def _get_bases_default(type_):
        bases = _bases(type_)
        if bases is None:
            return None
        return tuple((i.typing, i.class_) for i in bases)
elif PY_OLD:
    def _get_bases_default(type_):
        if type_ in _BUILTIN_LINKS.class_:
            return _get_bases_class(type_)
        else:
            return _get_bases_typing(type_)
else:
    def _get_bases_default(type_):
        return _get_bases_class(type_)


if PY_35 and VERSION <= (3, 5, 0):
    def _bases(type_):
        type_ = _FROM_CLASS.get(type_, type_)
        origins = _safe_getattr_tuple(type_, '__bases__')
        if not origins:
            return None
        mro = ()
        for orig in origins:
            t = get_type_info(orig)
            if t is None:
                raise ValueError('{}, {}'.format(t, type_))
            mro += _BaseObj(
                t.typing,
                t.class_,
                orig if len(t.args) > len(t.parameters) else None
            ),
        return mro
else:
    def _bases(type_):
        base_defaults = _get_bases_default(type_)
        if base_defaults is None:
            return ()

        orig_bases = {}
        for base in _safe_getattr_tuple(type_, '__orig_bases__'):
            _, class_ = get_typing(base)
            orig_bases.setdefault(class_, []).append(base)

        orig_bases = {k: iter(v) for k, v in orig_bases.items()}

        sentinel = object()
        bases = ()
        for typing_, class_ in base_defaults:
            if class_ not in orig_bases:
                bases += _BaseObj(typing_, class_, None),
                continue
            b = next(orig_bases[class_], sentinel)
            if b is sentinel:
                del orig_bases[class_]
                bases += _BaseObj(typing_, class_, None),
            else:
                bases += _BaseObj(typing_, class_, b),

        left_over = [i for lst in orig_bases.values() for i in lst]
        if left_over:
            print(base_defaults, orig_bases)
            raise ValueError('Did not consume all orig_bases for the class provided. {}'.format(left_over))
        return bases


def get_bases(type_):
    t = get_type_info(type_)
    if t is None:
        return _bases(type_)
    if not t.args or t.class_ not in _BUILTIN_LINKS.class_:
        return _bases(t.class_)
    bases = ()
    for base in _bases(t.class_):
        if base.class_ not in _BUILTIN_LINKS.class_:
            bases += base,
        else:
            p = get_parameters(base.typing)
            if p:
                bases += _BaseObj(base.typing, base.class_, base.typing[t.args[:len(p)]]),
            else:
                bases += base,
    return bases


def _get_parents(type_):
    parents = ()
    for base in get_bases(type_):
        parents += base,
        b = base.class_ if base.orig is None else base.orig
        parents += _get_parents(b)
    return parents


def get_parents(type_):
    t = get_type_info(type_)
    if t is None:
        typing_, class_, orig = _FROM_CLASS.get(type_, type_), _FROM_TYPING.get(type_, type_), None
    else:
        typing_, class_ = t.typing, t.class_
        orig = type_ if t.args else None
    return (_BaseObj(typing_, class_, orig),) + _get_parents(type_)


def _inner_set(values):
    vs = zip(*values)
    return [set(v) for v in vs]


def get_mro_orig(type_):
    parents = {}
    for parent in get_parents(type_):
        parents.setdefault(parent.class_, []).append(parent)

    mro = ()
    for class_ in get_mro(type_):
        if class_ not in parents:
            mro += _BaseObj(_FROM_CLASS.get(class_, class_), class_, None),
            continue

        classes = parents.pop(class_)
        if not all(a.typing is b.typing for a, b in pairwise(classes)):
            raise ValueError('MRO has two different types using the same class')

        if all(c.orig is None for c in classes):
            mro += classes[0],
            continue

        args = _inner_set(get_args(c.orig) if c.orig is not None else {} for c in classes)
        new_args = ()
        for arg in args:
            if not args:
                raise ValueError('One argument is empty')
            if len(arg) == 1:
                new_args += arg.pop(),
            else:
                new_args += typing.Union[tuple(arg)],
        c = classes[0]
        mro += _BaseObj(c.typing, c.class_, c.typing[new_args]),

    if parents:
        raise ValueError("Didn't consume all parents")

    return mro
