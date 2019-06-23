"""Get TypeVar info."""

import collections
import typing


_TypeVarInfo = collections.namedtuple(
    'TypeVarInfo',
    ['name', 'constraints', 'bound', 'covariant', 'contravariant'],
)


def get_type_var_info(type_var):
    """
    Get information in a TypeVar.

    .. doctest::

        >>> TExample = TypeVar('TExample', bound=int)

        >>> t_example = get_type_var_info(TExample)
        >>> t_example
        TypeVarInfo(name='TExample', constraints=(), bound=<class 'int'>, covariant=False, contravariant=False)
        >>> t_example.name
        'TExample'
        >>> t_example.bound
        <class 'int'>
        >>> t_example.covariant
        False
        >>> t_example.contravariant
        False
    """
    if not isinstance(type_var, typing.TypeVar):
        raise TypeError('get_type_var_info must be passed a TypeVar')
    return _TypeVarInfo(
        getattr(type_var, '__name__', None),
        getattr(type_var, '__constraints__', None),
        getattr(type_var, '__bound__', None),
        getattr(type_var, '__covariant__', None),
        getattr(type_var, '__contravariant__', None),
    )
