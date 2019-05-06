import collections
import typing


_TypeVarInfo = collections.namedtuple('TypeVarInfo', ['name', 'bound', 'covariant', 'contravariant'])


def get_type_var_info(tv):
    """
    Get information in a TypeVar

    Example:

        TExample = TypeVar('TExample', bound=int)

        t_example = get_type_var_info(TExample)
        t_example == ('TExample', int, False, False)
        t_example.name == 'TExample'
        t_example.bound == int
        t_example.covariant is False
        t_example.contravariant is False
    """
    if not isinstance(tv, typing.TypeVar):
        raise TypeError('get_type_var_info must be passed a TypeVar')
    return _TypeVarInfo(
        getattr(tv, '__name__', None),
        getattr(tv, '__bound__', None),
        getattr(tv, '__covariant__', None),
        getattr(tv, '__contravariant__', None)
    )