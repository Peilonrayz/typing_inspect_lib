import typing
import types
import collections
import itertools
try:
    import typing_extensions
except ImportError:
    pass

from .links import VERSION, PY_35, PY_OLD, LITERAL_TYPES, CLASS_TYPES, TYPING_TYPES, TYPING_TO_CLASS, CLASS_TO_TYPING, SP_CLASS_TYPES_WRAPPED, SP_TYPING_TYPES
from ._compat import typing_


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


def _get_last_origin(type_):
    if hasattr(type_, '_gorg'):
        return type_._gorg

    origins = _get_origins(type_)
    if len(origins) > 1:
        return origins[-1]
    return None


# Get typing code

if PY_OLD:
    def _get_typing(type_):
        origin = _get_last_origin(type_)
        if origin is not None:
            return origin, TYPING_TO_CLASS[origin] or origin

        if isinstance(type_, typing.GenericMeta):
            return type_, type_
        return None
else:
    def _get_typing(type_):
        origin = getattr(type_, '__origin__', None)
        if origin is not None:
            return CLASS_TO_TYPING[origin] or origin, origin

        if hasattr(type_, '__orig_bases__'):
            return type_, type_
        return None


def _get_special_typing_universal(type_):
    if isinstance(type_, typing.TypeVar):
        return typing.TypeVar, type_
    if isinstance(type_, typing_.ProtocolMeta):
        return typing_.Protocol, type_
    if isinstance(type_, types.FunctionType) and hasattr(type_, '__supertype__'):
        return typing_.NewType, type_
    return None


if PY_OLD:
    def _get_special_typing(type_):
        return SP_CLASS_TYPES_WRAPPED[type(type_)]
else:
    def _get_special_typing(type_):
        return None


def get_typing(type_):
    ret = (
            _get_special_typing_universal(type_)
            or LITERAL_TYPES[type_]
            or CLASS_TYPES[type_]
            or TYPING_TYPES[type_]
            or _get_typing(type_)
            or _get_special_typing(type_)
    )
    if ret is None:
        return None, None
    t, c = ret
    if t is typing_.NewType:
        c = type_
    return t, c


def get_special_type(type_):
    t_typing = get_typing(type_)[0]
    if t_typing in SP_TYPING_TYPES:
        return t_typing
    return None


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
